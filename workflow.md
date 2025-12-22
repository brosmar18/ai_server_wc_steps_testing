# AI Server - System Architecture & Workflow

> **A comprehensive guide to the AI-powered CSV import mapping system**

---

## 🔄 Complete Processing Workflow

### **Stage 1: File Upload & Preparation** 📁

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant FileSystem
    
    User->>Frontend: Select object & CSV file
    Frontend->>Backend: POST /upload/csv
    Backend->>FileSystem: Save to ImportFiles directory
    FileSystem-->>Backend: File saved ✓
    Backend->>Backend: Parse CSV header
    Note over Backend: Extract column names<br/>["Employee Number", "Email", ...]
```

**Details:**
- **File Location**: `{UPLOAD_DIRECTORY}/{filename}`
- **Example**: `C:\...\ImportFiles\employees.csv`
- **Validation**: CSV format, file size.
- **Result**: Object name is used to get schema. Column names extracted for mapping. File name is used to create import in the final step.

---

### **Stage 2: Schema Fetching** 🗄️

```mermaid
sequenceDiagram
    participant Backend
    participant CDATA
    
    Backend->>CDATA: GET /simpleFilters?object=employee
    CDATA-->>Backend: Raw field definitions (42 fields)
    Backend->>Backend: Format fields
    Note over Backend: Clean structure:<br/>field_name, field_label,<br/>field_type, ref_object_name
```

**Details:**
- **Endpoint**: `/rest/web/advancedFilter/simpleFilters`
- **Response**: Complete object schema with all fields
- **Processing**: Transform to AI-friendly format
- **Example Output**:
  ```json
    Example:
        Input (raw CDATA):
        [
            {
                "fieldName": "empno",
                "label": "Emp No",
                "fieldType": "string",
                "options": {
                    "title": "Employee Number",
                    "altVarName": "",
                    "fieldOrVar": "field",
                    "length": 26,
                    "required": true,
                }
            }
        ]
        
        Output (formatted):
        [
            {
                "field_name": "empno",
                "field_label": "Emp No",
                "field_type": "string",
                "whats_this": "Employee Number"
            }
        ]
  ```

---

### **Stage 3: AI Parent Object Mapping** 🤖

```mermaid
flowchart LR
    Input[CSV Columns +<br/>Object Fields] --> Agent[AI Agent<br/>]
    Agent --> Analysis{Analyze Each<br/>Column}
    Analysis --> Simple[Simple Fields<br/>Direct mapping]
    Analysis --> Reference[Reference Fields<br/>Need lookup]
    Simple --> Output1[Mappings<br/>column → fieldName]
    Reference --> Output2[Ref Mappings<br/>column → ref_object]
    
    style Agent fill:#10A37F,color:#fff
    style Analysis fill:#181F67,color:#fff
```

**AI Agent Configuration:**
```python
Agent(
    name="Field Mapping Agent",
    instructions="""Expert at CSV to database field mapping.
    Analyze column names and field definitions to find best matches.""",
    response_format=MappingObject  # Structured Pydantic output
)
```

**Example Mappings:**
| CSV Column | Field Name | Type | Notes |
|------------|------------|------|-------|
| Employee Number | `empno` | string | Direct mapping |
| Email | `email` | email | Direct mapping |
| Primary Job Title | `emptitle` | reference | → emptitle object |
| Department | `shift` | reference | → shift object |

---

### **Stage 4: Parallel Reference Processing** ⚡ 

```mermaid
flowchart TB
    Start[Reference Fields<br/>Identified] --> Fetch[Fetch All<br/>Ref Schemas]
    
    Fetch --> Parallel{asyncio.gather<br/>PARALLEL EXECUTION}
    
    Parallel --> AI1[AI Call 1<br/>Job Title → emptitle]
    Parallel --> AI2[AI Call 2<br/>Shift → shift]
    Parallel --> AI3[AI Call N<br/>...]
    
    AI1 --> Result1[field: 'emptitle']
    AI2 --> Result2[field: 'shift']
    AI3 --> Result3[field: '...']
    
    Result1 --> Combine[Combine with<br/>Metadata]
    Result2 --> Combine
    Result3 --> Combine
    
    Combine --> Final[Complete Reference<br/>Mappings]
    
    style Parallel fill:#FF6B6B,color:#fff
    style Start fill:#7BB837
    style Final fill:#7BB837
```

#### **Step 4a: Fetch Reference Schemas**

```mermaid
sequenceDiagram
    participant Backend
    participant CDATA
    
    par Fetch jobtitle
        Backend->>CDATA: GET /simpleFilters?object=emptitle
        CDATA-->>Backend: emptitle fields
    and Fetch shift
        Backend->>CDATA: GET /simpleFilters?object=shift
        CDATA-->>Backend: shift fields
    end
    
    Note over Backend: ref_schemas = {<br/>  "emptitle": [...],<br/>  "shift": [...]<br/>}
```

#### **Step 4b: Build Parallel Prompts**

For **each** reference field:
1. Create individual prompt with column + ref object fields
2. Store metadata: `(column_name, ref_object, parent_field)`

**Example:**
- Prompt 1: Map "Primary Job Title" → jobtitle fields
- Prompt 2: Map "Department" → department fields

#### **Step 4c: Execute in Parallel** 

```python
# 🚀 THE MAGIC: All AI calls run simultaneously
results = await asyncio.gather(
    Runner.run(agent, prompt1),  # "Primary Job Title"
    Runner.run(agent, prompt2),  # "Shift"
    # ... N prompts, all parallel
)
```


#### **Step 4d: Combine Results**

```python
# Zip metadata with AI results
for (column, ref_obj, parent_field), result in zip(metadata, results):
    ref_obj_ai_mappings[column] = {
        "column": column,
        "parent_field_name": parent_field,
        "field_name": result.field_name,  # From AI
        "ref_object_name": ref_obj
    }
```

---

### **Stage 5: Import Configuration** ⚙️

```mermaid
flowchart LR
    Mappings[All Mappings<br/>Simple + Reference] --> Builder[Config Builder]
    Builder --> Simple[Simple Fields<br/>col + fieldName]
    Builder --> Ref[Reference Fields<br/>+ lookupRefObject<br/>+ lookupFieldName<br/>+ createOnMissing: true]
    Simple --> Config[Import Params]
    Ref --> Config
    Config --> Metadata[+ Import Name<br/>+ Description<br/>+ Instructions]
    
    style Builder fill:#181F67,color:#fff
    style Config fill:#7BB837
```

**Field Override Structure:**

**Simple Field:**
```json
{
  "col": 0,
  "fieldName": "empno"
}
```

**Reference Field:**
```json
{
  "col": 4,
  "fieldName": "emptitle",
  "lookupRefObject": "jobtitle",
  "lookupFieldName": "title",
  "createOnMissing": true  // ✓ Always true for references
}
```

---

### **Stage 6: CDATA Import Creation** 🎯

#### Payload Example: 
```json
{
  "params": {
    "fieldOverrides": [
      {
        "col": 0,
        "fieldName": "equipno"
      },
      {
        "col": 1,
        "fieldName": "assettype",
        "lookupRefObject": "assettype",
        "lookupFieldName": "descr",
        "createOnMissing": true
      },
      {
        "col": 2,
        "fieldName": "make",
        "lookupRefObject": "eqmake",
        "lookupFieldName": "make",
        "createOnMissing": true
      },
      {
        "col": 4,
        "fieldName": "model",
        "lookupRefObject": "eqmodel",
        "lookupFieldName": "model",
        "createOnMissing": true
      },
      {
        "col": 5,
        "fieldName": "equipstatus",
        "lookupRefObject": "equipstatus",
        "lookupFieldName": "equipstatus",
        "createOnMissing": true
      },
      {
        "col": 6,
        "fieldName": "purdate"
      }
    ],
    "importName": "Asset AI Atlas",
    "importDescription": "Asset info from AI",
    "importInstructions": "Load data from equip_ai.csv."
  }
}
```

**Details:**
- **Endpoint**: `/rest/web/import/saveImport/builder:{object}/{file}`
- **Auth**: Basic authentication (username, password)
- **Lookup Field**: First fieldOverride's fieldName
- **Graceful Failure**: Returns error but continues processing

---

