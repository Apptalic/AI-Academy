from langchain.prompts import PromptTemplate
from langchain.agents import Tool, AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import warnings

load_dotenv()

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Tool 1: Content Cleaner
def clean_content_tool(raw_text):
  prompt_template = PromptTemplate(
    input_variables=["content"],
    template=(
            "You are an expert content cleaner. Your task is to clean the following text by removing any unrelated or unwanted data, "
            "such as navigation links, advertisements, social media prompts, or footer text. Ensure the content is concise, focused, "
            "and ready for further processing. Preserve the core content and structure while removing distractions.\n\n"
            "Content:\n{content}\n\n"
            "Return the cleaned content, ensuring it is well-structured and free of irrelevant elements."
    ),
  )
  llm=ChatOpenAI(model="gpt-4o", temperature="0.3", api_key=os.getenv("OPENAI_API_KEY"))
  chain = prompt_template | llm
  return chain.invoke({"content": raw_text})


# Tool 2: Content Validator
def validate_content_tool(cleaned_text):
  prompt_template = PromptTemplate(
    input_variables=["content"],
    template=(
            "You are an expert content validator. Analyze the following text and determine if it is meaningful, well-structured, "
            "and suitable for generating a mini-course. If the content is valid, return 'Valid Content' along with a brief summary "
            "of why it is suitable. If the content is not valid, return 'Invalid Content' and provide actionable feedback on how "
            "to improve it for mini-course generation.\n\n"
            "Content:\n{content}\n\n"
            "Validation Result:"
    ),
  ) 
  llm=ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
  chain = prompt_template | llm
  result = chain.invoke({"content": cleaned_text})

  if "Invalid Content" in result:
    feedback = result.split('Invalid Content:')[1].strip()
    return {"valid": False, "feedback": feedback}
  else:
    return {"valid": True, "content": cleaned_text}
  

# Tool 3: Content improver
def improve_content_tool(invalid_content, feedback):
  prompt_template = PromptTemplate(
    input_variables=["content", "feedback"],
    template=(
            "You are an expert content editor. The following content has been deemed invalid for generating a mini-course. "
            "Your task is to improve the content based on the provided feedback so that it becomes valid and suitable for mini-course generation.\n\n"
            "Content:\n{content}\n\n"
            "Feedback:\n{feedback}\n\n"
            "Return the improved content, ensuring it is well-structured, meaningful, and ready for mini-course generation."
    ),
  ) 
  llm=ChatOpenAI(model="gpt-4o", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
  chain = prompt_template | llm
  return chain.invoke({"content": invalid_content, "feedback": feedback})

# Tool 4: Mini-course generator tool
def mini_generator_tool(validated_text):
  prompt_template = PromptTemplate(
    input_variables=["content"],
    template=(
            "You are an professional course creator. Your task is to create a single, fully detailed, and publish-ready mini-course "
            "from the following content. The mini-course should follow this structure:\n\n"
            "1. **Title**: A concise and engaging title for the mini-course.\n"
            "2. **Introduction**: A well detailed overview explaining the purpose of the mini-course and what learners will achieve.\n"
            "3. **Key Learning Objectives**: A list of 3-5 specific, actionable objectives that learners will accomplish by the end of the mini-course.\n"
            "4. **Detailed Content**: A well written, structured explanation of the topic, divided into sections with headings. Each section should include:\n"
            "   - A heading for the section.\n"
            "   - A detailed explanation of the topic.\n"
            "   - Examples, practical applications, or actionable steps where relevant.\n"
            "5. **Engagement Elements**: Suggest 1-2 interactive elements (e.g., activities, discussion prompts, or reflection questions) to engage learners and reinforce the material.\n"
            "6. **Quiz**: Create a quiz with 5-7 questions based on the content. Include a mix of question types (e.g., multiple-choice, true/false, and short-answer questions). Ensure the questions are directly tied to the learning objectives.\n\n"
            "Ensure the mini-course is grammatically correct, clear, professional, and ready for publishing and be detailed as possible. ALWAYS Return the mini-course in a structured markdown format.\n\n"
            "Content:\n{content}\n\n"
            "ALWAYS Return the mini-course in a structured format, clearly separating each section with headings and bullet points for easy readability."
      ),
  )
  llm=ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))
  chain = prompt_template | llm
  return chain.invoke({"content": validated_text})


# Define Tools for Agent
clean_content = Tool(
  name="Content Cleaning",
  func=clean_content_tool,
  description="Cleans raw text by removing unwanted data such as navigation links, ads and unrelated text."
)

validate_content = Tool(
  name="Content Validation",
  func=validate_content_tool,
  description="Validates cleaned text to ensure it is meaningful and suitable for mini-course generation."
)

improve_content = Tool(
  name="Improve Content",
  func=improve_content_tool,
  description="Improves invalid content based on validation feedback to make it suitable for mini-course generation."
)

generate_mini_courses = Tool(
  name="Mini-course generation",
  func=mini_generator_tool,
  description="Generates mini-courses from validated text, including titles, summaries, objectives and quizzes."
)


# Init the Agent
def create_agent():
  tools = [clean_content, validate_content, improve_content, generate_mini_courses]
  llm = ChatOpenAI(model="gpt-4o", temperature=0.5, api_key=os.getenv("OPENAI_API_KEY"))

  system_message = """You are an expert agent that processes raw content into mini-courses.
  CRITICAL INSTRUCTION: You must follow these steps exactly:
  1. Use the tools to process the content (clean, validate, improve if needed)
  2. Generate the mini-course using the Mini-course generation tool
  3. Your final response MUST BE the complete mini-course content exactly as generated, with NO modifications or summaries
  4. DO NOT add any commentary or status messages about the mini-course
  5. ONLY return the mini-course content in markdown format
  
  Example of correct final response:
  # Mini-Course Title
  
  ## Introduction
  [introduction content]
  
  ## Learning Objectives
  [objectives content]

  ## Course 
  [Course content]
  ...
  """

  agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, #ReACt
    verbose=True,
    handle_parsing_errors=True,
    system_message=system_message,
    return_direct=True
  )

  return agent

# Wrapper to get the mini-course from the agent 
def get_mini_course(raw_text):
    agent = create_agent()
    result = agent(
        {
            "input": f"""Process this content into a mini-course. 
            Your response must ONLY be the complete mini-course content in markdown format:
            
            {raw_text}"""
        }
    )
    # If result is a non-empty string, return it
    if isinstance(result, str) and len(result.strip()) > 0:
        return result.strip()
    # If result is a dict, try to get the output key
    if isinstance(result, dict):
        content = result.get('output', '')
        if content and len(content.strip()) > 0:
            return content.strip()
    # Fallback
    return "Error: Could not generate mini-course content. Please try again."



# To test the agent
# def main():
#     raw_content = """
#     Home | About | Contact
#     Sponsored: Buy cheap widgets at example.com
#     ----
#     Python decorators are a concise way to modify function behavior.
#     They wrap a function and can add pre- or post-processing.
#     Example: measure execution time of a function.
#     ----
#     Footer: © 2025 Example Inc. Follow us on social!
#     """

#     print("=== RAW CONTENT ===")
#     print(raw_content.strip(), "\n")

#     agent = create_agent()

#     try:
#         mini_course = get_mini_course(raw_content)
#         print("=== AGENT OUTPUT (Mini-course) ===")
#         print(mini_course)
#     except Exception as e:
#         print("Error generating course:", e)

# if __name__ == "__main__":
#     main()