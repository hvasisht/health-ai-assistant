"""
Load medical documents into ChromaDB
"""

import os
from medical_knowledge import MedicalKnowledgeRAG

def load_all_documents():
    """Load all medical documents into ChromaDB."""
    
    print("🔄 Loading medical documents into ChromaDB...\n")
    
    # Initialize RAG
    rag = MedicalKnowledgeRAG()
    
    # Document directory
    docs_dir = os.path.join(os.path.dirname(__file__), 'documents')
    
    document_count = 0
    
    # Load ADA Guidelines
    print("📚 Loading ADA Guidelines...")
    ada_dir = os.path.join(docs_dir, 'ada_guidelines')
    if os.path.exists(ada_dir):
        for filename in os.listdir(ada_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(ada_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                doc_id = f"ada_{filename.replace('.txt', '')}"
                metadata = {
                    'source': 'ADA Guidelines 2024',
                    'category': 'guidelines',
                    'filename': filename
                }
                
                rag.add_document(content, metadata, doc_id)
                document_count += 1
                print(f"  ✓ Loaded: {filename}")
    
    # Load Glycemic Index
    print("\n📚 Loading Glycemic Index Database...")
    gi_dir = os.path.join(docs_dir, 'glycemic_index')
    if os.path.exists(gi_dir):
        for filename in os.listdir(gi_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(gi_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                doc_id = f"gi_{filename.replace('.txt', '')}"
                metadata = {
                    'source': 'Glycemic Index Database',
                    'category': 'nutrition',
                    'filename': filename
                }
                
                rag.add_document(content, metadata, doc_id)
                document_count += 1
                print(f"  ✓ Loaded: {filename}")
    
    # Load Exercise Safety
    print("\n📚 Loading Exercise Safety Guidelines...")
    exercise_dir = os.path.join(docs_dir, 'exercise_safety')
    if os.path.exists(exercise_dir):
        for filename in os.listdir(exercise_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(exercise_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                doc_id = f"exercise_{filename.replace('.txt', '')}"
                metadata = {
                    'source': 'ADA Exercise Guidelines',
                    'category': 'exercise',
                    'filename': filename
                }
                
                rag.add_document(content, metadata, doc_id)
                document_count += 1
                print(f"  ✓ Loaded: {filename}")
    
    # Load Medications
    print("\n📚 Loading Medication Information...")
    meds_dir = os.path.join(docs_dir, 'medications')
    if os.path.exists(meds_dir):
        for filename in os.listdir(meds_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(meds_dir, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                doc_id = f"med_{filename.replace('.txt', '')}"
                metadata = {
                    'source': 'Medication Database',
                    'category': 'medications',
                    'filename': filename
                }
                
                rag.add_document(content, metadata, doc_id)
                document_count += 1
                print(f"  ✓ Loaded: {filename}")
    
    print("\n" + "="*60)
    print(f"✅ Successfully loaded {document_count} documents into ChromaDB!")
    print("="*60)
    print("\n💡 You can now use RAG in your agents!")
    
    # Test retrieval
    print("\n🧪 Testing retrieval...\n")
    
    test_query = "What are the target glucose ranges?"
    print(f"Query: '{test_query}'")
    context = rag.get_context(test_query, n_results=1)
    print(context)

if __name__ == "__main__":
    load_all_documents()