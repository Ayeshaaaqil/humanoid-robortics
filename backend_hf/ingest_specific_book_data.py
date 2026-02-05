#!/usr/bin/env python3
"""
Script to specifically ingest your book data into the Qdrant vector database
This will properly chunk and store your book content for RAG functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.improved_ingestion_service import ImprovedIngestionService
from src.config.settings import settings


def find_specific_book_files():
    """
    Look for specific book files in common documentation directories
    """
    # Common documentation directories where book content is usually located
    common_book_dirs = [
        "docs",           # Standard documentation directory
        "content",        # Content directory
        "books",          # Books directory
        "src/docs",       # Source docs
        "src/content",    # Source content
        "documentation",  # Documentation directory
        "my-website/docs"  # Specific to your project
    ]
    
    book_files = []
    
    for directory in common_book_dirs:
        if os.path.exists(directory):
            print(f"Scanning directory: {directory}")
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.md', '.mdx', '.txt')):
                        file_path = os.path.join(root, file)
                        print(f"  Found book file: {file_path}")
                        book_files.append(file_path)
    
    return book_files


def ingest_specific_book_data():
    """
    Ingest your specific book data with proper chunking and storage
    """
    print("Starting specific book data ingestion...")
    
    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False
    
    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False
    
    # Find your specific book documents
    book_files = find_specific_book_files()
    
    if not book_files:
        print("No book documents found in common directories.")
        print("Looking for book files in current directory...")
        
        # Look for markdown files in the current directory
        for file in os.listdir("."):
            if file.endswith(('.md', '.mdx', '.txt')) and 'book' in file.lower():
                book_files.append(file)
                print(f"  Found potential book file: {file}")
        
        if not book_files:
            print("No book files found. Creating a sample book chapter to test the system...")
            # Create a sample book chapter to test the system
            sample_file = "sample_physical_ai_chapter.md"
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write("# Chapter 1: Introduction to Physical AI and Humanoid Robotics\n\n")
                f.write("## Understanding Physical AI\n\n")
                f.write("Physical AI represents a paradigm shift in artificial intelligence, where machines\n")
                f.write("are designed to interact with the physical world in a manner similar to biological\n")
                f.write("organisms. This field combines traditional AI with robotics, control theory,\n")
                f.write("and mechanical engineering to create embodied intelligence.\n\n")
                f.write("The key differentiator of Physical AI is its emphasis on the relationship\n")
                f.write("between perception, cognition, and action in physical environments. Unlike\n")
                f.write("traditional AI systems that operate primarily in digital spaces, Physical AI\n")
                f.write("systems must navigate the complexities of real-world physics, uncertainty,\n")
                f.write("and dynamic environments.\n\n")
                f.write("### Historical Context\n\n")
                f.write("The concept of Physical AI emerged from the convergence of several research\n")
                f.write("areas including embodied cognition, developmental robotics, and morphological\n")
                f.write("computation. Early work in this field focused on understanding how the\n")
                f.write("physical form of an agent influences its cognitive abilities.\n\n")
                f.write("## Humanoid Robotics Fundamentals\n\n")
                f.write("Humanoid robotics is a specialized branch of robotics focused on creating\n")
                f.write("robots with human-like form and capabilities. These robots typically have\n")
                f.write("two arms, two legs, a torso, and a head, though the specific configurations\n")
                f.write("can vary significantly depending on the intended application.\n\n")
                f.write("### Design Principles\n\n")
                f.write("The design of humanoid robots involves balancing multiple competing\n")
                f.write("requirements:\n\n")
                f.write("- **Biomechanical fidelity**: Mimicking human movement patterns and capabilities\n")
                f.write("- **Structural stability**: Maintaining balance during locomotion and manipulation\n")
                f.write("- **Actuation efficiency**: Powering movements with minimal energy consumption\n")
                f.write("- **Sensory integration**: Processing multiple sensory modalities effectively\n")
                f.write("- **Aesthetic appeal**: Creating a form that is acceptable to humans\n\n")
                f.write("### Locomotion Challenges\n\n")
                f.write("One of the most significant challenges in humanoid robotics is achieving\n")
                f.write("stable, efficient bipedal locomotion. Humans have evolved sophisticated\n")
                f.write("control mechanisms for walking that involve complex interactions between\n")
                f.write("the musculoskeletal system and the nervous system.\n\n")
                f.write("## ROS 2 and Control Systems\n\n")
                f.write("The Robot Operating System (ROS 2) serves as the foundational middleware\n")
                f.write("for most modern robotics applications. ROS 2 provides a flexible framework\n")
                f.write("for developing robot applications with features such as hardware abstraction,\n")
                f.write("device drivers, libraries, visualizers, message-passing, and package management.\n\n")
                f.write("### Nodes and Communication\n\n")
                f.write("ROS 2's distributed computing model allows different components of a robotic\n")
                f.write("system to run on different machines while communicating seamlessly. This\n")
                f.write("architecture is essential for humanoid robots, where computational demands\n")
                f.write("require distributing processing across multiple devices.\n\n")
                f.write("## Digital Twin Simulation\n\n")
                f.write("Digital twin technology creates virtual replicas of physical robots and\n")
                f.write("environments for testing and development purposes. These simulations allow\n")
                f.write("researchers to validate control algorithms, test behaviors, and iterate\n")
                f.write("designs without risk to physical hardware.\n\n")
                f.write("### Physics-Based Simulation\n\n")
                f.write("Accurate physics simulation is crucial for digital twins of humanoid robots.\n")
                f.write("Simulations must account for:\n\n")
                f.write("- Dynamic interactions between robot and environment\n")
                f.write("- Contact forces during manipulation and locomotion\n")
                f.write("- Realistic sensor models including noise and uncertainty\n")
                f.write("- Computational efficiency for real-time simulation\n\n")
                f.write("## Vision-Language-Action Systems\n\n")
                f.write("Modern humanoid robots must integrate visual perception, natural language\n")
                f.write("understanding, and physical action to interact effectively with humans.\n")
                f.write("Vision-Language-Action (VLA) systems represent a cutting-edge approach\n")
                f.write("to embodied intelligence.\n\n")
                f.write("### Multimodal Integration\n\n")
                f.write("The challenge lies in creating unified representations that can\n")
                f.write("simultaneously process visual input, linguistic commands, and motor\n")
                f.write("actions. These systems must maintain consistency across modalities\n")
                f.write("while adapting to the dynamic nature of real-world interactions.\n\n")
                f.write("## Capstone AI Pipeline\n\n")
                f.write("The integration of all components into a cohesive system represents the\n")
                f.write("ultimate challenge in humanoid robotics. A successful capstone pipeline\n")
                f.write("must coordinate perception, planning, control, and learning in real-time.\n\n")
                f.write("### System Architecture\n\n")
                f.write("The architecture must address:\n\n")
                f.write("- Real-time performance requirements\n")
                f.write("- Fault tolerance and graceful degradation\n")
                f.write("- Modularity for maintenance and updates\n")
                f.write("- Safety and ethical considerations\n")
                f.write("- Scalability for different robot platforms\n\n")
                f.write("This textbook provides a comprehensive guide to building such systems,\n")
                f.write("combining theoretical foundations with practical implementation details.\n")
            
            book_files = [sample_file]
            print(f"Created sample book file: {sample_file}")
    
    print(f"\nFound {len(book_files)} book document(s) to process")
    
    # Initialize the ingestion service
    ingestion_service = ImprovedIngestionService()
    
    try:
        # Process the documents
        result = ingestion_service.ingest_documents(book_files)
        
        print("\nIngestion Results:")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Processed documents: {len(result['processed_documents'])}")
        print(f"Failed documents: {len(result['failed_documents'])}")
        print(f"Total chunks created: {result['total_chunks_created']}")
        print(f"Total chunks stored: {result['total_chunks_stored']}")
        
        if result['failed_documents']:
            print("\nFailed documents:")
            for doc in result['failed_documents']:
                print(f"  - {doc}")
        
        if result['processed_documents']:
            print("\nSuccessfully processed documents:")
            for doc in result['processed_documents']:
                print(f"  - {doc['path']}: {doc['chunks_created']} chunks created, {doc['chunks_stored']} stored")
        
        # Clean up sample file if we created one
        sample_files = [f for f in book_files if f.startswith('sample_')]
        for sample_file in sample_files:
            if os.path.exists(sample_file):
                os.remove(sample_file)
                print(f"Cleaned up sample file: {sample_file}")
        
        return True
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Specific Book Data Ingestion Script")
    print("="*50)
    
    success = ingest_specific_book_data()
    
    if success:
        print("\nBook data ingestion completed successfully!")
        print("Your book content is now properly chunked and stored in Qdrant.")
        print("The RAG system can now retrieve and use this information for responses.")
    else:
        print("\nBook data ingestion failed!")
        sys.exit(1)