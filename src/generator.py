from langchain_groq import ChatGroq
from PyPDF2 import PdfReader
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from io import BytesIO
import traceback
import os
from dotenv import load_dotenv

class emailGenerator():
    def __init__(self, job_url, document):
        load_dotenv()
        try:
            self.llm = ChatGroq(
                            model_name= "llama-3.1-70b-versatile",
                            temperature=0,
                            # groq_api_key=st.secrets["groq_api_key"]  
                            groq_api_key= os.getenv("groq_api_key")  
                    )
        except TypeError as e:
            print("Error: ", e)
            print(traceback.format_exc())
        # self.ignore = st.secrets['ignore']
        self.ignore = os.getenv('ignore')
        # self.comp_ignore = st.secrets['comp_ignore']
        self.comp_ignore = os.getenv('comp_ignore')
        self.job_url = job_url
        self.file = document
        

    def load(self):

        self.file.file.seek(0)  
        file_content = self.file.file.read()  # Read the entire file content as bytes

        # Create a BytesIO stream
        pdf_stream = BytesIO(file_content)

        # Use PdfReader with the BytesIO stream
        pdfreader = PdfReader(pdf_stream)

        count = len(pdfreader.pages)
        all_page_text = ""
        for i in range(count):
            page = pdfreader.pages[i]
            all_page_text += page.extract_text()
            
        return all_page_text
        
    def jobPosting(self):
        loader = WebBaseLoader(self.job_url)
        page_data = loader.load().pop().page_content
        

        job_prompt = PromptTemplate.from_template(
            """
            ## Scrapped text from Website:
            {page_data}
            ## INSTRUCTION:
            The scraped text is from the career's page of a website.
            You job is to extract the job postions and return them in JSON format containg
            following keys: 'role', 'experience', 'skills' and 'description'.
            only return the valid JSON.
            ## VAILD JSON (NO PREAMBLE):

        """
        )
        job_extract = job_prompt | self.llm
        res = job_extract.invoke(input={'page_data': page_data})
        Json_parser = JsonOutputParser()
        json_res = Json_parser.parse(res.content)
        return json_res

    def main(self):
        
        job_extract = self.jobPosting()
        
        resume_extract = self.load()
        
        return job_extract, resume_extract
    
    def email(self, resume, page_data):

        # page_data,  resume = self.main()
        
        prompt_extract = PromptTemplate.from_template(
            """
            ## Scrapped text from resume:
            from my resume {resume}
            ## INSTRUCTION:
            Scraped is the data which it a bit about my career experince,
            and the resume.
            my name is xyz, I am currently in boston. review the job
            information in {page_data}, and draft me an cold email to be the hiring 
            manger for that job. And donot mention my email and other contact details.
            Never mention the name {ignore} and {comp_ignore}
        """
        )
        chain_extract = prompt_extract | self.llm
        generatedEmail = chain_extract.invoke(input={'page_data': page_data,  
                                                    'resume':resume,
                                                    'ignore': self.ignore,
                                                    'comp_ignore': self.comp_ignore})

        return generatedEmail.content

    def run(self):
        try:
            job, resume = self.main()
            print("Running email generation...")
            generated_email = self.email(resume, job)
            

        except Exception as e:
            import traceback
            print("Error in email generation: ", traceback.format_exc())
            raise e
            
        return generated_email