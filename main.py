import os
from crewai import Task, Crew
from dotenv import load_dotenv
import pathlib
from datetime import datetime
import traceback

# Import from our modules
from crew_definition import agents
from logging_config import generate_pdf_report, save_analysis_results

# Load environment variables
load_dotenv()

print("Starting CV Writer script...")

# Set OpenAI API key directly
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
os.environ["OPENAI_MODEL_NAME"] = "gpt-4"

print("Environment variables set...")

def create_tasks(jd_url: str, resume_path: str) -> list[Task]:
    tasks = []
    
    # Task 1: Job Type Analysis
    task1 = Task(
        description=(
            f"Analyze {jd_url} and provide:\n"
            "1. Role Category: IT/Product/Hybrid (with % split)\n"
            "2. Primary Technical Requirements (ranked)\n"
            "3. Primary Business Requirements (ranked)\n"
            "4. Domain Expertise Needs (prioritized)\n"
            "Output Format: JSON with categories and scores"
        ),
        expected_output="JSON containing role category, technical requirements, business requirements, and domain expertise",
        agent=agents[0]  # job_type_analyzer
    )
    
    # Task 2: Job Requirements
    task2 = Task(
        description=(
            f"Using job type analysis, extract from {jd_url}:\n"
            "1. Must-have skills (ranked by importance)\n"
            "2. Experience requirements (with metrics)\n"
            "3. Key performance expectations\n"
            "4. Technical vs business skill ratio\n"
            "Output Format: Structured list with priority scores"
        ),
        expected_output="Structured list of job requirements with priority scores and metrics",
        agent=agents[1],  # jd_scraper
        dependencies=[task1]
    )
    
    # Task 3: Resume Analysis
    task3 = Task(
        description=(
            f"Create skills matrix from {resume_path}:\n"
            "1. Technical skills (with proficiency 1-10)\n"
            "2. Business capabilities (with evidence)\n"
            "3. Project metrics and impact\n"
            "4. Leadership experience metrics\n"
            "Output Format: JSON skills matrix"
        ),
        expected_output="JSON skills matrix with technical skills, business capabilities, project metrics, and leadership metrics",
        agent=agents[2]  # resume_analyser
    )
    
    # Task 4: Fit Analysis
    task4 = Task(
        description=(
            "Calculate candidate fit metrics:\n"
            "1. Overall match score (0-100)\n"
            "2. Technical skills match (%)\n"
            "3. Business skills match (%)\n"
            "4. Experience level match (%)\n"
            "Output Format: JSON with match scores"
        ),
        expected_output="JSON containing overall match score and specific skill match percentages",
        agent=agents[3],  # fit_analyzer
        dependencies=[task1, task2, task3]
    )
    
    # Task 5: CV Optimization
    task5 = Task(
        description=(
            "Optimize CV based on analysis:\n"
            "1. Highlight matching skills (prioritized)\n"
            "2. Quantify relevant achievements\n"
            "3. Add missing keywords\n"
            "4. Restructure for role alignment\n"
            "Output Format: Structured CV content"
        ),
        expected_output="Structured CV content with optimized skills, achievements, and keywords",
        agent=agents[4],  # cv_updater
        dependencies=[task2, task4]
    )
    
    # Task 6: Skills Profile
    task6 = Task(
        description=(
            "Create ATS-optimized skills profile:\n"
            "1. Map skills to requirements (with scores)\n"
            "2. Add missing critical skills\n"
            "3. Optimize keyword density\n"
            "4. Format for ATS scanning\n"
            "Output Format: ATS-friendly skills section"
        ),
        expected_output="ATS-optimized skills profile with mapped requirements and keyword optimization",
        agent=agents[5],  # cv_content_optimizer
        dependencies=[task4, task5]
    )
    
    # Task 7: Initial PDF Generation
    task7 = Task(
        description=(
            "Generate initial PDFs:\n"
            "1. Analysis report with metrics\n"
            "2. Updated CV with optimized format\n"
            "3. Skills matrix visualization\n"
            "4. Recommendations summary\n"
            "Output Format: Two PDFs (report and CV)"
        ),
        expected_output="Two PDF files: analysis report and updated CV",
        agent=agents[6],  # pdf_generator
        dependencies=[task1, task2, task3, task4, task5, task6]
    )
    
    # Task 8: Interview Preparation
    task8 = Task(
        description=(
            "Prepare interview materials:\n"
            "1. Technical interview questions\n"
            "2. Behavioral interview questions\n"
            "3. Role-specific scenario questions\n"
            "4. Suggested answer frameworks\n"
            "5. Key talking points based on resume-job alignment"
        ),
        expected_output="Comprehensive interview preparation guide with questions and answer frameworks",
        agent=agents[7],  # interview_prep_agent
        dependencies=[task1, task2, task3, task4]
    )
    
    # Task 9: Final PDF Report Generation
    task9 = Task(
        description=(
            "Generate final professional PDF reports:\n"
            "1. Analysis Report including:\n"
            "   - Role Classification\n"
            "   - Job Requirements Analysis\n"
            "   - Skills Matrix\n"
            "   - Match Analysis\n"
            "   - Interview Guide\n"
            "2. Updated CV including:\n"
            "   - Professional Summary\n"
            "   - Optimized Skills Section\n"
            "   - Relevant Experience\n"
            "   - Achievements\n"
            "Format: Professional PDFs with clear sections, proper formatting, and ATS-friendly layout"
        ),
        expected_output="Two professional PDF documents: Analysis Report and Updated CV",
        agent=agents[8],  # pdf_report_generator
        dependencies=[task1, task2, task3, task4, task5, task6, task7, task8]
    )
    
    # Add all tasks to the list in order
    tasks.extend([task1, task2, task3, task4, task5, task6, task7, task8, task9])
    
    return tasks

def analyze_job_and_resume(jd_url: str, resume_path: str):
    try:
        resume_file = pathlib.Path(resume_path)
        if not resume_file.exists():
            raise FileNotFoundError(f"Resume file not found at: {resume_path}")
        
        print("Starting analysis pipeline...")
        
        tasks = create_tasks(jd_url, str(resume_file))
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            process_type="sequential"  # Ensure sequential processing
        )
        
        print("Executing analysis pipeline...")
        result = crew.kickoff()
        
        if result and hasattr(result, 'tasks_output'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "Job_Application_Analysis"
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                # Debug print to see what we're getting
                print("\nTask outputs received:")
                for i, output in enumerate(result.tasks_output):
                    print(f"Task {i + 1}: {'Available' if output else 'Not available'}")
                
                # Save raw analysis results
                results_file = save_analysis_results(output_dir, result.tasks_output, timestamp)
                print(f"\nRaw analysis results saved to: {results_file}")
                
                # Generate PDFs using the helper function
                try:
                    print("\nGenerating PDF reports...")
                    analysis_pdf, cv_pdf = generate_pdf_report(
                        output_dir=output_dir,
                        tasks_output=result.tasks_output,
                        timestamp=timestamp
                    )
                    print(f"Analysis report generated: {analysis_pdf}")
                    print(f"Updated CV generated: {cv_pdf}")
                except Exception as pdf_error:
                    print(f"Error during PDF generation: {str(pdf_error)}")
                    traceback.print_exc()
                
            except Exception as e:
                print(f"Error in file operations: {str(e)}")
                traceback.print_exc()
            
        return result
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        # Use the Google Program Manager job URL and your CV path
        jd_url = "https://www.google.com/about/careers/applications/jobs/results/96851973449360070-program-manager-strategic-business-operations"
        resume_path = r"C:\Users\Charan s\Downloads\CV - Charan Sai Germany.pdf"
        
        print("\nAnalyzing job posting and resume...")
        print(f"Job URL: {jd_url}")
        print(f"Resume path: {resume_path}")
        
        result = analyze_job_and_resume(jd_url, resume_path)
        
        if result and hasattr(result, 'tasks_output') and result.tasks_output:
            print("\nAnalysis completed successfully!")
            print("Check the Job_Application_Analysis directory for:")
            print("1. Raw analysis results (analysis_results_*.txt)")
            print("2. Analysis report PDF (analysis_report_*.pdf)")
            print("3. Updated CV PDF (updated_cv_*.pdf)")
        else:
            print("\nAnalysis failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"\nUnexpected error in main: {str(e)}")
        traceback.print_exc()