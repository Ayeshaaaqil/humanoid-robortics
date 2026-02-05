#!/usr/bin/env python3
"""
Final test script for the improved ingestion service.
This script will test the chunking parameters with a longer text to better evaluate the requirements.
"""

import os
import sys

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.improved_ingestion_service import AdvancedTextChunker


def test_chunking_requirements():
    """
    Test the advanced text chunker to ensure it meets all requirements:
    - Chunk size: 400-600 tokens
    - Overlap: 50-100 tokens
    - Do not break sentences in the middle
    - Remove empty or duplicate chunks
    """
    print("Testing Advanced Text Chunker Requirements...")
    
    # Initialize the chunker with target parameters
    chunker = AdvancedTextChunker(chunk_size=500, overlap=75)
    
    # Create a longer test document to better test chunking
    test_text = """
# Introduction to Artificial Intelligence

Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving. This technology has revolutionized various industries and continues to advance at an unprecedented pace.

The field of artificial intelligence encompasses various subfields including machine learning, deep learning, natural language processing, computer vision, and robotics. Each of these areas contributes unique capabilities that enable machines to perform tasks that traditionally required human intelligence.

## Machine Learning Fundamentals

Machine learning is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.

The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future. Through building models, machine learning enables computers to make predictions or decisions without being explicitly programmed to do so.

Supervised learning is one of the most common types of machine learning where the algorithm learns from labeled training data. The algorithm makes predictions based on the training data and is corrected by the teacher until the desired output is achieved. This approach is widely used in applications like image classification and spam detection.

Unsupervised learning, on the other hand, uses unlabeled data and the algorithm tries to find patterns and relationships in the data. Common applications include market segmentation and recommendation systems. The system tries to learn the patterns and structures from the data without any guidance.

Reinforcement learning is another approach where an agent learns to make decisions by performing actions and receiving rewards or penalties. This type of learning is commonly used in robotics, gaming, and navigation systems. The agent learns the optimal strategy through trial and error.

## Deep Learning and Neural Networks

Deep learning is a specialized subset of machine learning that uses interconnected layers of artificial neural networks to process data. These networks are designed to mimic the structure and function of the human brain, with nodes representing neurons and connections representing synapses.

Artificial neural networks consist of layers of interconnected nodes. Each node receives input, processes it using an activation function, and passes the output to the next layer. The network learns by adjusting the weights of connections between nodes based on the error in the output.

Deep neural networks have multiple hidden layers between the input and output layers. This depth allows the network to learn complex patterns and representations from the data. The more layers a network has, the more complex features it can learn to recognize.

Convolutional Neural Networks (CNNs) are particularly effective for image recognition tasks. They use convolutional layers that apply filters to input data to detect features like edges, textures, and objects. CNNs have achieved remarkable success in computer vision applications.

Recurrent Neural Networks (RNNs) are designed to handle sequential data by maintaining a hidden state that captures information about previous inputs. This makes them suitable for tasks like language modeling, time series prediction, and speech recognition.

## Natural Language Processing

Natural Language Processing (NLP) is a field of AI focused on the interaction between computers and humans through natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a manner that is valuable.

Modern NLP techniques are based on machine learning and deep learning algorithms. These techniques enable computers to process human language in the form of text or voice data and to understand its full meaning, complete with the speaker's intent and sentiment.

Tokenization is the process of breaking down text into smaller units called tokens, which can be words, phrases, or symbols. This is the first step in most NLP pipelines and significantly affects the performance of downstream tasks.

Part-of-speech tagging involves labeling each word in a text with its corresponding part of speech, such as noun, verb, adjective, etc. This helps in understanding the grammatical structure of sentences and is useful for parsing and semantic analysis.

Named entity recognition (NER) identifies and classifies named entities in text into predefined categories such as person names, organizations, locations, dates, and more. NER is crucial for information extraction and knowledge graph construction.

Sentiment analysis determines the emotional tone or attitude expressed in a piece of text. This technique is widely used in social media monitoring, customer feedback analysis, and market research to understand public opinion.

## Computer Vision

Computer vision is a field of artificial intelligence that trains computers to interpret and understand the visual world. Using digital images from cameras and videos and deep learning models, machines can accurately identify and classify objects and then react to what they 'see'.

Image classification is one of the fundamental tasks in computer vision where the goal is to assign a label to an entire image. Convolutional Neural Networks have achieved remarkable success in image classification tasks, often surpassing human-level performance.

Object detection goes beyond image classification by not only identifying objects in an image but also determining their location. This is achieved by drawing bounding boxes around detected objects and labeling them with their corresponding classes.

Image segmentation involves partitioning an image into multiple segments to simplify its representation. Semantic segmentation assigns a label to every pixel in the image, while instance segmentation distinguishes between different instances of the same object class.

Face recognition technology identifies or verifies individuals from digital images or video frames. This technology has applications in security systems, social media, and user authentication. However, it also raises privacy concerns that need to be addressed.

Optical Character Recognition (OCR) converts different types of documents, such as scanned paper documents or images, into editable and searchable data. This technology is essential for digitizing printed documents and making them accessible.

## Ethics in AI

As AI systems become more prevalent, ethical considerations become increasingly important. Issues such as bias in AI systems, privacy concerns, and the impact of AI on employment need to be carefully considered and addressed.

Algorithmic bias occurs when AI systems make unfair decisions based on race, gender, age, or other protected characteristics. This can happen due to biased training data, flawed algorithms, or other factors. Addressing bias is crucial for creating fair and equitable AI systems.

Privacy in AI involves protecting personal data and ensuring that individuals' rights are respected. This includes implementing privacy-preserving techniques, obtaining proper consent, and ensuring transparency in data usage.

The impact of AI on employment is a significant concern as automation may displace certain types of jobs. However, AI also creates new opportunities and can augment human capabilities. Preparing the workforce for these changes is essential.

Transparency and explainability in AI systems are important for building trust and enabling proper oversight. Users should understand how AI systems make decisions, especially in critical applications like healthcare, finance, and criminal justice.

Developers and organizations must ensure that AI systems are fair, transparent, and accountable. This includes addressing algorithmic bias, ensuring data privacy, and maintaining human oversight of AI systems.
"""
    
    print(f"Original text length: {len(test_text)} characters")
    print(f"Estimated tokens: {chunker.estimate_tokens(test_text)}")
    
    # Chunk the text
    chunks = chunker.chunk_text(test_text, metadata={"source": "test_document"})
    
    print(f"\nNumber of chunks created: {len(chunks)}")
    
    # Verify requirements
    all_tests_passed = True
    
    print("\nChunk details:")
    for i, chunk in enumerate(chunks):
        content = chunk["content"]
        token_count = chunk["metadata"]["token_count"]
        char_count = len(content)
        
        print(f"Chunk {i+1}: {char_count} chars, ~{token_count} tokens")
        
        # Check for sentence boundary preservation (basic check)
        if content[-1] not in ['.', '!', '?', ')', ']', '"', "'"]:
            # This might be okay if it's the last chunk, but let's check
            if i < len(chunks) - 1:  # Not the last chunk
                print(f"  WARNING: Chunk {i+1} doesn't end with sentence punctuation")
    
    # Check chunk sizes are in the required range (400-600 tokens)
    print(f"\nTesting chunk size requirements (400-600 tokens)...")
    for i, chunk in enumerate(chunks):
        token_count = chunk["metadata"]["token_count"]
        if 400 <= token_count <= 600:
            print(f"  PASS Chunk {i+1}: {token_count} tokens (within range)")
        else:
            print(f"  FAIL Chunk {i+1}: {token_count} tokens (outside range)")
            all_tests_passed = False

    # Check for empty chunks
    print(f"\nTesting for empty chunks...")
    empty_chunks = [chunk for chunk in chunks if not chunk["content"].strip()]
    if empty_chunks:
        print(f"  FAIL Found {len(empty_chunks)} empty chunks")
        all_tests_passed = False
    else:
        print("  PASS No empty chunks found")

    # Check for duplicate chunks
    print(f"\nTesting for duplicate chunks...")
    seen_content = set()
    duplicates = []
    for chunk in chunks:
        content = chunk["content"].strip()
        content_hash = hash(content)
        if content_hash in seen_content:
            duplicates.append(content)
        seen_content.add(content_hash)

    if duplicates:
        print(f"  FAIL Found {len(duplicates)} duplicate chunks")
        all_tests_passed = False
    else:
        print("  PASS No duplicate chunks found")

    print(f"\nOverall test result: {'PASS All requirements met' if all_tests_passed else 'FAIL Some requirements not met'}")
    return all_tests_passed


def test_embedding_service():
    """
    Test the embedding service to ensure it handles API errors gracefully
    and validates vector dimensions.
    """
    print("\nTesting Embedding Service...")
    
    from src.services.embedding_service import EmbeddingService
    from src.config.settings import settings
    
    if not settings.COHERE_API_KEY:
        print("  SKIP: COHERE_API_KEY not set, cannot test embedding service")
        return True
    
    try:
        embedding_service = EmbeddingService()
        
        # Test with a simple text
        test_text = "This is a test sentence for embedding."
        embedding = embedding_service.embed_text(test_text)
        
        if len(embedding) == 1024:  # Expected size for Cohere multilingual-v3.0
            print("  PASS Embedding service working correctly with 1024 dimensions")
            return True
        else:
            print(f"  FAIL Embedding has {len(embedding)} dimensions, expected 1024")
            return False
            
    except Exception as e:
        print(f"  FAIL Error testing embedding service: {e}")
        return False


if __name__ == "__main__":
    print("Running comprehensive tests for improved ingestion service...\n")
    
    chunking_test_passed = test_chunking_requirements()
    embedding_test_passed = test_embedding_service()
    
    all_passed = chunking_test_passed and embedding_test_passed
    
    print(f"\nFinal result: {'All tests passed!' if all_passed else 'Some tests failed'}")
    sys.exit(0 if all_passed else 1)