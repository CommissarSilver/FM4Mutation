
# Data Flow
1. Input Parameters: The `mutator.py` script accepts various command-line arguments such as project name, mutation type, number of mutants, and cache directory.
2. LLM Interaction: Using the `LLMInterface`, the system communicates with the configured LLM to generate mutated code based on the provided mutation type and source code.
3. Mutation Processing:
    - The original code is loaded from the cache.
    - The LLM applies the specified mutation and returns the mutated code in XML format.
    - The system parses the XML output to extract mutation details and the mutated code.
4. Storage: If enabled, the mutated code and data trails are saved in the designated directories for further analysis or testing.

# How to Run Mutator
1. Install Dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Environment: Ensure you have the necessary configurations set in `agent_config.yml`.

3. Execute the Mutator:
```bash
python mutator.py --project <PROJECT_NAME> --mutation <MUTATION_TYPE> --number_of_mutants <NUMBER> --store <True/False>
```
- Parameters:
    - `--project`: Name of the project (e.g., Cli-11).
    - `--mutation`: Type of mutation (e.g., AOD, AOR).
    - `--number_of_mutants`: Number of mutants to generate.
    - `--store`: Whether to store the mutated files.

# LLM Interface
The `LLMInterface` class facilitates interaction with the configured Language Model. It manages roles, handles conversation history, and processes responses from the LLM.

## Key Features
- Role Management: Set and retrieve roles to define the LLM's behavior.
- Conversation Handling: Maintain and clear conversation history.
- Interaction Templates: Utilize predefined templates for consistent communication with the LLM.

## Configuration for LLM Agent
Configurations are managed via the `agent_config.yml` file. This file defines prompts, interaction templates, and LLM-specific settings.

### Sections
- **prompts**: Define templates for different roles. For example, the mutator role includes instructions and mutation rules.
- **interaction_templates**: Specify required keys and templates for interactions. The mutator role includes a basic template for applying mutations.
- **llms**: Configure LLM settings such as model name, parameters (e.g., temperature, max tokens), and whether to use a local model.

## Example Configuration
```yaml
prompts:
  mutator:
    template: >
      You are an expert code mutation system designed to apply specific mutations to source code while preserving its functional intent...
      
interaction_templates:
  mutator:
    templates:
      - name: basic
        required_keys: [mutation, code]
        template: |
          Apply the following mutation to the given code snippet.
      
          Mutation: {mutation}
      
          Code:
          {code}
      
          **Important:** Provide only the XML output as specified, without additional explanations or text.

llms:
  mutator:
    model_name: gpt-4o-mini
    params:
      temperature: 0.8
      max_tokens: 5120
    local: false
```

## Customizing Configurations
- Adding New Roles: Define a new role under prompts and specify corresponding interaction templates and LLM settings.
- Modifying Mutation Rules: Update the template under the desired role in prompts to change mutation behaviors.
- Adjusting LLM Parameters: Tweak the params under the desired LLM in llms to control aspects like response creativity and length.
