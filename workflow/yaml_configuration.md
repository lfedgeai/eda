# YAML Configuration Files

This document describes the structure and usage of YAML configuration files in the EDA project.

## Overview

YAML configuration files are used to define:
1. **Agent Prompts** - System prompts for individual LLM agents
2. **Workflows** - Multi-step workflows that chain multiple agents together

## Agent Prompt Configuration

Agent prompt files define system prompts for individual LLM agents. These files follow a consistent structure:

### Structure

```yaml
name: <agent_name>
role: system
content: |
  <system_prompt_content>
```

### Fields

- **`name`** (required): The unique identifier for the agent (e.g., `file_reader`, `extract_metadata`, `rag_coding`)
- **`role`** (required): Typically set to `"system"` to indicate this is a system prompt
- **`content`** (required): The full system prompt text that defines the agent's role, instructions, input/output formats, and behavior

### Example

```yaml
name: file_reader
role: system
content: |
  **System Prompt for `file_reader` Agent**
  
  **Role:**
  You are `file_reader`, an intelligent agent specialized in processing 
  file-related requests by invoking a PDF reader function...
  
  [Additional instructions, input/output formats, etc.]
```

### Available Agent Prompts

- `file_reader.yaml` - Agent for reading PDF files and extracting text
- `extract_metadata.yaml` - Agent for extracting metadata from files
- `retrieve_table_of_contents.yaml` - Agent for identifying and extracting table of contents from documents
- `rag_coding.yaml` - Agent for generating RAG (Retrieval-Augmented Generation) code

## Workflow Configuration

Workflow files define multi-step processes that chain multiple agents together to accomplish complex tasks.

### Structure

```yaml
name: <workflow_name>
description: |
  <workflow_description>

steps:
  - step: <agent_name_1>
    description: |
      <step_description>
  
  - step: <agent_name_2>
    description: |
      <step_description>
  
  # Additional steps...
```

### Fields

- **`name`** (required): The unique identifier for the workflow
- **`description`** (required): A description of what the workflow accomplishes
- **`steps`** (required): A list of workflow steps, where each step:
  - **`step`**: The name of the agent to execute (must match an agent prompt file name)
  - **`description`**: A description of what this step does

### Example

```yaml
name: pdf_retrieval_workflow
description: |
  Multi-step workflow for generating documentation Q&A retrieval.

steps:
  - step: file_reader
    description: |
      Function calling the pdf reader to retrieve text

  - step: extract_metadata
    description: |
      Use LLM to extract the file metadata

  - step: retrieve_table_of_contents
    description: |
      Use LLM to read table of contents if there is any

  - step: rag_coding
    description: |
      Write up the rag code for the document pdf
```

### Available Workflows

- `pdf_retrieval_workflow.yaml` - Multi-step workflow for generating documentation Q&A retrieval
- `presentation_workflow.yaml` - Multi-step workflow for generating educational presentations

## Usage in Code

YAML configuration files are loaded using Python's `yaml` library:

```python
import yaml

# Load an agent prompt
with open("workflow/file_reader.yaml", 'r') as stream:
    agent_config = yaml.safe_load(stream)
    agent_name = agent_config['name']
    system_prompt = agent_config['content']

# Load a workflow
with open("workflow/pdf_retrieval_workflow.yaml", 'r') as stream:
    workflow_config = yaml.safe_load(stream)
    workflow_name = workflow_config['name']
    steps = workflow_config['steps']
```

## Best Practices

1. **Naming Convention**: Use lowercase with underscores for agent and workflow names (e.g., `file_reader`, `pdf_retrieval_workflow`)
2. **Agent Prompts**: Include clear role definitions, detailed instructions, input/output format specifications, and error handling guidelines
3. **Workflow Steps**: Ensure step names match existing agent prompt file names
4. **Documentation**: Keep descriptions clear and concise, explaining what each agent/workflow does
5. **Consistency**: Follow the established structure for all configuration files

## File Locations

- Agent prompts: `workflow/*.yaml` (individual agent files)
- Workflows: `workflow/*_workflow.yaml` (workflow definition files)
