from langchain_community.document_loaders import PyPDFLoader

file_path = "G:\genai\langchain_basics_genai\loading_documents\sample_document1.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print(len(docs))