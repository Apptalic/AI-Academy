import ollama 
import os 
from typing import Dict, List, Tuple 
import traceback


class QuestionnareAgent:
  def __init__(self, model_name: str = "llama3.1:8b"):
    self.model_name = model_name
    self.document_path = "documents"
    self.client = ollama.Client(host='http://localhost:11434')

  def read_documents(self) -> Dict[str, str]:
    documents = {}
    for filename in os.listdir(self.document_path):
      if filename.endswith('.txt'):
        with open(os.path.join(self.document_path, filename), 'r') as f:
          documents[filename] = f.read()
    return documents
  
  def generate_question(self, text:str) -> List[str]:
    text_lenth = len(text)
    num_questions = min(max(3, text_lenth//1000), 7)

    max_length = 6000
    if len(text) > max_length:
      text = text[:max_length] + '...'

    prompt = f"""
    Based on the following text, generate {num_questions} questions that test understanding of the key concepts. 
    Format each question on a new line, ending with a question mark. Make questions progressively harder.

    Text: {text}
    """

    try: 
      print("Generating questions... This may take a moment.")
      client = ollama.Client(host='http://localhost:11434')
      response = client.chat(
        model=self.model_name,
        messages=[
          {
            "role": "user",
            "content": prompt
          }
        ],
        options={
          "temperature" : 0.7,
          "num_predict": 1000,
        }
      )

      questions = []
      for line in response['message']['content'].split('\n'):
        line = line.strip()
        for prefix in ['Q:', 'Question:', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.']:
            if line.startswith(prefix):
                line = line[len(prefix):].strip()
        if line and '?' in line:
            questions.append(line)           

      if not questions:
        print("No valid questions generated. Response was: ", response['message']['content'])
        return []
      
      return questions[:num_questions] 
      
    except Exception as e:
      print(f"Error generating questions: {e}")
      print("Full error details:")
      traceback.print_exc()
      return []
    

  def evaluate_answer(self, text: str, question: str, answer: str) -> str:
    eval_prompt = f"""
      Based on this text: {text}

        Question: {question}
        User's Answer: {answer}

        Evaluate if the answer is correct. Respond in this format:
        [CORRECT/INCORRECT] Brief explanation why, including the correct answer if wrong.
    """

    try: 
      client = ollama.Client(host='http://localhost:11434')
      response = client.chat(
          model=self.model_name,
          messages=[{"role": "user", "content": eval_prompt}],
          options={
              "temperature": 0.2,  
              "num_predict": 200
          }
      )
      return response['message']['content']
    
    except Exception as e:
      return f"Error evalauting answer: {e}"
    
  def run_question_agent(self):
    print("Welcome to the AI Questionnare Agent!")
    print("Reading documents from the documents folder... \n")

    documents = self.read_documents()
    if not documents:
      print("No text document found. Please a text document to the folder.")
      return 
    
    for filename, content in documents.items():
      print(f"\n Processing documents: {filename}")
      print("="*50)

      question_list = self.generate_question(content)
      if not question_list:
        print(f"Could not generate questions for {filename}")
        continue

      correct_count = 0 
      for i, question in enumerate(question_list, 1):
        print(f"\nQuestion {i}/{len(question_list)}:")
        print(question)

        user_answer = input("\nYour answer: ").strip()
        if not user_answer:
            print("Skipping question...")
            continue
        
        feedback = self.evaluate_answer(content, question, user_answer)
        print("\nFeedback:", feedback)

        if feedback.strip().upper().startswith("[CORRECT]"):
          correct_count += 1
        elif "[PARTIALLY CORRECT]" in feedback.upper():
          print("Partial credit score doesn't count towards the final score")


      score = (correct_count / len(question)) * 100
      print(f"\nYou got {correct_count} out of {len(question_list)} questions correct ({score:.1f}%)")
      print("Note: Only fully correct answers are counted in the score.")
      print("="*50)

if __name__ == "__main__":
  agent = QuestionnareAgent()
  agent.run_question_agent()
