from langchain.prompts import PromptTemplate

prompt= '''
Given the information provided in the following resume, extract the details and return them in the specified JSON format:

Resume:
{resume}

JSON Format:
{{
  "name": "<Full Name>",
  "email": "<Email Address>",
  "skills": ["<Skill 1>", "<Skill 2>", "<Skill 3>", ...],
  "certificates": ["<Certificate Name 1>", "<Certificate Name 2>", ...],
  "education": ["<School Name 1>-<Diploma/Degree>", "<School Name 2>-<Diploma/Degree>", ...],
  "experiences": ["<Company Name 1>-<Position>", "<Company Name 2>-<Position>", ...]
}}

Ensure the JSON is formatted correctly and includes all relevant details from the resume. Don't add any additional information that is not present in the specified JSON format.

'''
template=""" Given the following list of candidates:

{context}

And the query: "{question}"

Return only the list of indexes, name, and email of the candidates that are most relevant to the query, formatted as a array of dictionaries.Do not include any introductions or explanations, just the array.

"""

refined_template = """
Given the following list of candidates:
{context}

The query: "{question}"

And the preliminary answer: "{answer}" (a list of indexes, names, and emails of initially selected candidates).

Analyze the suitability of each candidate in the preliminary answer based on the query. Consider the following weights for each factor:
- Education: {education}
- Experience: {experience}
- Skills: {skills}
- Certifications: {certificates}

Official certifications that are relevant to the query should be considered as a positive factor.

Return a final refined list, formatted as an array of dictionaries, including only the indexes, names, emails of the most suitable candidates and a "why" column explaining briefly why you chose that candidate.

Only return the list of candidates that are most suitable based on the query. Do not include any introductions or explanations, just the array.
"""

rag_prompt = PromptTemplate.from_template(template)
refined_rag_prompt = PromptTemplate.from_template(refined_template)
json_loader_prompt=PromptTemplate.from_template(prompt)
