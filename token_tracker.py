from typing import Optional
import os

from openai import OpenAI
from dotenv import load_dotenv
import tiktoken


TOTAL_TOKENS = 1000
REMAINING_TOKENS = TOTAL_TOKENS

load_dotenv()

def tokenCounter(
        user_prompt:Optional[str],
        model:str="gpt-4o"
)->int:
    enc = tiktoken.encoding_for_model(model)
    token_count=enc.encode(user_prompt or "")
    return len(token_count)

def isExceded(
        user_input_token_count
)->bool:
    is_exceeded = False
    # Tokens Remaining after the user prompt
    tokens_left = REMAINING_TOKENS - user_input_token_count
    # Check if the user prompt tokens exceeds remaining tokens
    if(tokens_left<=0):
        print(" no extra tokens to print the response ")
        print(f"Total tokens remaining are {REMAINING_TOKENS}")
        is_exceeded=True
    return is_exceeded

def sendToLLM(
        user_prompt:str,
        REMAINING_TOKENS:int
)->dict:
    base_url=os.getenv("BASE_URL")
    try:
        client = OpenAI(base_url=base_url)
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {
                    "role" : "system",
                    "content":"you are an expert geek of technology"
                },
                {
                    "role": "developer",
                    "content": """
                    You must always answer the user’s query in 3 parts: 
                    (1) What it is, (2) Why it is used, and (3) Where it is used.  
                    Before generating the response, you must check how many tokens are remaining.  
                    Remainig token Limit : {REMAINING_TOKENs}

                    If the full 3-part explanation requires more tokens than the remaining token limit,
                    you must compress or shorten the response to fit only within the remaining tokens.  
                    Only when absolutely necessary, you may use up all remaining tokens, but never exceed them."""
                },
                {
                    "role" : "user",
                    "content":user_prompt
                },
            ]
        )
        # extracting the response message 
        response_message = response.choices[0].message.content
        # extracting the completion_token_count
        completion_token_count = response.usage.completion_tokens
        # extracting the total_tokens_count
        total_tokens_count = response.usage.total_tokens
        # extracting the prompt_token_count
        prompt_token_count = response.usage.prompt_tokens
        
        return {
            "messages" : response_message,
            "usages":{
                "completion_token_count":completion_token_count,
                "total_tokens_count":total_tokens_count,
                "prompt_token_count":prompt_token_count
            }
        } 
    except Exception as e:
        return {
            "messages" : e,
            "usages":{
                "completion_token_count":0,
                "total_tokens_count":0,
                "prompt_token_count":0
            }
        }
        
    
while True:
    # taking the user prompt
    user_prompt =input("enter your question or enter q to exit : ")
    # Exit when user enters q
    if user_prompt.lower()=="q":
        break
    user_input_token_count = tokenCounter(user_prompt=user_prompt)
   
    if isExceded(user_input_token_count):
        continue
    response_obj = sendToLLM(user_prompt=user_prompt,REMAINING_TOKENS=REMAINING_TOKENS)
   # if(response_obj["usages"]["total_tokens_count"] > REMAINING_TOKENS):
    # print(" no extra tokens to generate the response ")
     # print(f"Total tokens remaining are {REMAINING_TOKENS}")"""
    REMAINING_TOKENS =REMAINING_TOKENS - response_obj["usages"]["total_tokens_count"]
    print(f"LLM response for the query :  {response_obj['messages']}")
    print(f"total_tokens_count : {response_obj["usages"]["total_tokens_count"]}")
    print(f"prompt_token_count : {response_obj["usages"]["prompt_token_count"]}")
    print(f"completion_token_count : {response_obj["usages"]["completion_token_count"]}")

    print(f"Remaining Token count : {REMAINING_TOKENS}")







        


    
   

