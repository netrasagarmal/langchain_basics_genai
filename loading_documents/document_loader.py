from abc import ABC, abstractmethod
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.documents import Document
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from exceptions import UnsupportedFileTypeError, FileLoadError, InvalidConfigurationError


# Abstract Base Class
class DocumentLoader(ABC):
    """Abstract base class for document loaders"""
    
    @abstractmethod
    def load(self) -> List[Document]:
        """Load documents without splitting"""
        pass
    
    @abstractmethod
    def load_and_split(self, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
        """Load documents and split them"""
        pass

# Concrete Implementations
class PDFDocumentLoader(DocumentLoader):
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.file_path = file_path
        self.loader = PyPDFLoader(file_path)
    
    def load(self) -> List[Document]:
        try:
            return self.loader.load()
        except Exception as e:
            raise FileLoadError(f"Error loading PDF file: {str(e)}")
    
    def load_and_split(self, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
        try:
            return self.loader.load_and_split(text_splitter=text_splitter)
        except Exception as e:
            raise FileLoadError(f"Error loading and splitting PDF file: {str(e)}")

class DOCXDocumentLoader(DocumentLoader):
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = file_path
        self.loader = Docx2txtLoader(file_path)
    
    def load(self) -> List[Document]:
        try:
            return self.loader.load()
        except Exception as e:
            raise FileLoadError(f"Error loading DOCX file: {str(e)}")
    
    def load_and_split(self, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
        try:
            return self.loader.load_and_split(text_splitter=text_splitter)
        except Exception as e:
            raise FileLoadError(f"Error loading and splitting DOCX file: {str(e)}")

class TXTDocumentLoader(DocumentLoader):
    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = file_path
        self.loader = TextLoader(file_path)
    
    def load(self) -> List[Document]:
        try:
            return self.loader.load()
        except Exception as e:
            raise FileLoadError(f"Error loading TXT file: {str(e)}")
    
    def load_and_split(self, text_splitter: RecursiveCharacterTextSplitter) -> List[Document]:
        try:
            return self.loader.load_and_split(text_splitter=text_splitter)
        except Exception as e:
            raise FileLoadError(f"Error loading and splitting TXT file: {str(e)}")

# Factory Class
class DocumentLoaderFactory:
    """Factory class for creating document loaders based on file type"""
    
    @staticmethod
    def create_loader(file_path: str) -> DocumentLoader:
        """Create appropriate document loader based on file extension"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return PDFDocumentLoader(file_path)
        elif ext == '.docx':
            return DOCXDocumentLoader(file_path)
        elif ext == '.txt':
            return TXTDocumentLoader(file_path)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file type: {ext}")

# Configuration Class (Strategy Pattern)
class DocumentProcessorConfig:
    """Configuration class for document processing options"""
    
    def __init__(self, chunk_size: int = 100, chunk_overlap: int = 20):
        if chunk_size <= 0:
            raise InvalidConfigurationError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise InvalidConfigurationError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise InvalidConfigurationError("chunk_overlap must be smaller than chunk_size")
            
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        """Factory method for creating text splitter with current configuration"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

# Facade Pattern for simplified interface
class DocumentProcessor:
    """Facade for document loading and processing"""
    
    def __init__(self, config: Optional[DocumentProcessorConfig] = None):
        self.config = config or DocumentProcessorConfig()
    
    def process_document(self, file_path: str, load_and_split: bool = True) -> List[Document]:
        """Process document based on configuration"""
        try:
            loader = DocumentLoaderFactory.create_loader(file_path)
            
            if load_and_split:
                text_splitter = self.config.create_text_splitter()
                return loader.load_and_split(text_splitter)
            else:
                return loader.load()
                
        except FileNotFoundError as e:
            raise FileLoadError(f"Document processing failed: {str(e)}")
        except UnsupportedFileTypeError as e:
            raise FileLoadError(f"Document processing failed: {str(e)}")
        except Exception as e:
            raise FileLoadError(f"Unexpected error during document processing: {str(e)}")

# Example Usage
if __name__ == "__main__":
    try:
        # Configuration
        config = DocumentProcessorConfig(chunk_size=150, chunk_overlap=30)
        processor = DocumentProcessor(config)
        
        # Process different file types
        pdf_docs = processor.process_document("/path/to/document.pdf")
        docx_docs = processor.process_document("/path/to/document.docx", load_and_split=False)
        txt_docs = processor.process_document("/path/to/document.txt")
        
        print(f"Loaded {len(pdf_docs)} PDF document chunks")
        print(f"Loaded {len(docx_docs)} DOCX documents (unsplit)")
        print(f"Loaded {len(txt_docs)} TXT document chunks")
        
    except FileLoadError as e:
        print(f"Error processing document: {str(e)}")
    except InvalidConfigurationError as e:
        print(f"Invalid configuration: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")