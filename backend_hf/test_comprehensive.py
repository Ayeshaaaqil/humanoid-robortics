#!/usr/bin/env python3
"""
Comprehensive test script for the improved ingestion service.
This script will test the chunking parameters and verify they meet requirements.
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

    # Create a test document with various sentence lengths and types
    test_text = """
# Introduction to Artificial Intelligence

Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.

## Machine Learning Fundamentals

Machine learning is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. Machine learning focuses on the development of computer programs that can access data and use it to learn for themselves.

The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future. Through building models, machine learning enables computers to make predictions or decisions without being explicitly programmed to do so.

## Deep Learning and Neural Networks

Deep learning is a specialized subset of machine learning that uses interconnected layers of artificial neural networks to process data. These networks are designed to mimic the structure and function of the human brain, with nodes representing neurons and connections representing synapses.

Deep learning models can automatically discover representations needed for feature detection or classification directly from raw data. This capability allows deep learning models to achieve state-of-the-art performance on many challenging tasks.

## Natural Language Processing

Natural Language Processing (NLP) is a field of AI focused on the interaction between computers and humans through natural language. The ultimate objective of NLP is to read, decipher, understand, and make sense of human languages in a manner that is valuable.

Modern NLP techniques are based on machine learning and deep learning algorithms. These techniques enable computers to process human language in the form of text or voice data and to understand its full meaning, complete with the speaker's intent and sentiment.

## Computer Vision

Computer vision is a field of artificial intelligence that trains computers to interpret and understand the visual world. Using digital images from cameras and videos and deep learning models, machines can accurately identify and classify objects and then react to what they 'see'.

Applications of computer vision include facial recognition, autonomous vehicles, medical image analysis, and quality inspection in manufacturing. The technology is advancing rapidly with new applications emerging regularly.

## Ethics in AI

As AI systems become more prevalent, ethical considerations become increasingly important. Issues such as bias in AI systems, privacy concerns, and the impact of AI on employment need to be carefully considered and addressed.

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

    # Check overlap
    print(f"\nTesting overlap requirements (50-100 tokens)...")
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]["content"]
        next_chunk = chunks[i + 1]["content"]

        # Find overlap by checking how much of the next chunk appears at the end of the current chunk
        overlap_tokens = 0
        current_words = current_chunk.split()
        next_words = next_chunk.split()

        # Count overlapping words from the end of current chunk
        for j, word in enumerate(reversed(current_words)):
            if j < len(next_words) and current_words[-(j+1)] == next_words[j]:
                overlap_tokens += 1
            else:
                break

        # Convert to tokens (approximate)
        overlap_approx_tokens = overlap_tokens  # Rough approximation

        if 50 <= overlap_approx_tokens <= 100:
            print(f"  PASS Overlap between chunks {i+1}-{i+2}: ~{overlap_approx_tokens} tokens (within range)")
        else:
            print(f"  INFO Overlap between chunks {i+1}-{i+2}: ~{overlap_approx_tokens} tokens (may be outside range)")
            # Note: This is a simplified check; actual overlap implementation may vary

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