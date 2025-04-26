import os
from crewai import Agent
from crewai_tools import ScrapeWebsiteTool
from typing import Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
import pathlib

# Define schema for PDF reader
class PDFReaderSchema(BaseModel):
    pdf_path: str = Field(description="Path to the PDF file to read")

class PDFReaderTool(BaseTool):
    """Tool that reads PDF files."""
    name: str = "PDFReaderTool"
    description: str = "A tool that reads PDF files and extracts their text content"
    args_schema: Type[BaseModel] = PDFReaderSchema
    return_direct: bool = True

    def _run(self, pdf_path: str) -> str:
        try:
            pdf_path = pathlib.Path(pdf_path)
            if not pdf_path.exists():
                return f"Error: File not found at {pdf_path}"
            
            with fitz.open(str(pdf_path)) as doc:
                text = []
                for page in doc:
                    text.append(page.get_text("text"))
                return "\n".join(text) if text else "No text found in the PDF."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    async def _arun(self, pdf_path: str) -> str:
        return self._run(pdf_path)

# Initialize tools
pdf_reader_tool = PDFReaderTool()
scraper_tool = ScrapeWebsiteTool()

# Define Agents
jd_scraper = Agent(
    role="Job Description Analyzer",
    goal="Extract critical job requirements and create a structured analysis of technical, managerial, and soft skills needed",
    backstory=(
        "Expert in job requirement analysis with deep understanding of both technical and business roles. "
        "Skilled at identifying core competencies, must-have qualifications, and distinguishing between "
        "essential and preferred requirements. Experienced in ATS systems and keyword optimization."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[scraper_tool]
)

resume_analyser = Agent(
    role="Resume Analysis Expert",
    goal="Create a comprehensive skills matrix mapping candidate's experience to job requirements",
    backstory=(
        "Senior talent assessment specialist with expertise in skills gap analysis. "
        "Proficient in identifying transferable skills and quantifying achievements. "
        "Experienced in evaluating both technical capabilities and leadership potential."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[pdf_reader_tool]
)

job_type_analyzer = Agent(
    role="Role Classification Specialist",
    goal="Determine role category and provide detailed breakdown of role components (IT/Product/Hybrid)",
    backstory=(
        "Industry classification expert with extensive knowledge of modern job roles. "
        "Specialized in analyzing cross-functional positions and identifying primary vs secondary role aspects. "
        "Expert in modern tech industry role structures and organizational patterns."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[scraper_tool]
)

fit_analyzer = Agent(
    role="Candidate-Role Match Specialist",
    goal="Provide data-driven fit analysis with specific alignment scores for key job requirements",
    backstory=(
        "Expert in predictive hiring analytics with focus on role-candidate alignment. "
        "Skilled at quantifying candidate potential and identifying growth opportunities. "
        "Specializes in evidence-based hiring recommendations and gap analysis."
    ),
    verbose=True,
    allow_delegation=False
)

cv_updater = Agent(
    role="Strategic CV Optimization Expert",
    goal="Transform CV content to maximize alignment with target role while maintaining authenticity",
    backstory=(
        "Senior CV optimization specialist with expertise in ATS optimization and personal branding. "
        "Skilled at restructuring experiences to highlight relevant achievements and capabilities. "
        "Expert in modern CV best practices and industry-specific formatting."
    ),
    verbose=True,
    allow_delegation=False
)

cv_content_optimizer = Agent(
    role="Skills Alignment Specialist",
    goal="Create targeted skills profile matching job requirements with quantifiable achievements",
    backstory=(
        "Expert in skills-based resume optimization and ATS keyword matching. "
        "Specialized in translating experience into relevant competencies and achievements. "
        "Proficient in industry-specific terminology and competency frameworks."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[scraper_tool, pdf_reader_tool]
)

pdf_generator = Agent(
    role="Document Generation Specialist",
    goal="Create ATS-optimized, professionally formatted PDF documents with clear information hierarchy",
    backstory=(
        "Expert in professional document design and ATS-compatible formatting. "
        "Specialized in creating clear, scannable documents that highlight key information. "
        "Proficient in modern resume design principles and accessibility standards."
    ),
    verbose=True,
    allow_delegation=False
)

interview_prep_agent = Agent(
    role="Interview Preparation Specialist",
    goal="Create comprehensive interview preparation guide with targeted questions and suggested answers",
    backstory=(
        "Expert interview coach with deep experience in technical and business role preparation. "
        "Specialized in predicting interview questions based on job requirements and creating "
        "strategic response frameworks. Skilled at identifying key discussion points and potential challenges."
    ),
    verbose=True,
    allow_delegation=False
)

pdf_report_generator = Agent(
    role="PDF Report Generator",
    goal="Create professional PDF reports for analysis results and updated CV",
    backstory=(
        "Expert document formatter specializing in professional report generation. "
        "Skilled at organizing complex analysis data into clear, readable PDF documents. "
        "Experienced in creating ATS-friendly CV layouts and comprehensive analysis reports. "
        "Proficient in data visualization and professional document design."
    ),
    verbose=True,
    allow_delegation=False
)

# List of all agents for easy import
agents = [
    job_type_analyzer,
    jd_scraper,
    resume_analyser,
    fit_analyzer,
    cv_updater,
    cv_content_optimizer,
    pdf_generator,
    interview_prep_agent,
    pdf_report_generator
]