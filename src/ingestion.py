"""
Data ingestion module for processing markdown notes, PDFs, and saved links
"""

import re
import json
import csv
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import markdown
from io import StringIO, BytesIO
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)

class DataIngestion:
    """Handles ingestion and processing of various data sources"""
    
    def __init__(self):
        self.processed_items = []
    
    def process_data(self, markdown_data: List[Dict] = None, links_data: Any = None, pdf_data: List[Dict] = None) -> List[Dict]:
        """
        Process all data sources and return unified item list
        
        Args:
            markdown_data: List of markdown files with filename and content
            links_data: JSON/CSV data containing saved links
            pdf_data: List of PDF files with filename and content
            
        Returns:
            List of processed items with standardized structure
        """
        processed_items = []
        
        # Process markdown files
        if markdown_data:
            for md_file in markdown_data:
                items = self._process_markdown_file(md_file)
                processed_items.extend(items)
        
        # Process PDF files
        if pdf_data:
            for pdf_file in pdf_data:
                items = self._process_pdf_file(pdf_file)
                processed_items.extend(items)
        
        # Process links data
        if links_data:
            items = self._process_links_data(links_data)
            processed_items.extend(items)
        
        logger.info(f"Processed {len(processed_items)} total items")
        self.processed_items = processed_items
        return processed_items
    
    def _process_markdown_file(self, md_file: Dict) -> List[Dict]:
        """
        Extract structured data from a markdown file
        
        Args:
            md_file: Dict with 'filename' and 'content' keys
            
        Returns:
            List of processed items from the markdown file
        """
        filename = md_file['filename']
        content = md_file['content']
        
        # Generate unique ID based on filename and content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        item_id = f"md_{filename}_{content_hash}"
        
        # Extract title (first heading or filename)
        title = self._extract_title_from_markdown(content) or filename
        
        # Extract keywords and key phrases
        keywords = self._extract_keywords(content)
        
        # Convert markdown to plain text for better processing
        plain_text = self._markdown_to_text(content)
        
        # Create snippet (first 200 chars of content)
        snippet = plain_text[:200] + "..." if len(plain_text) > 200 else plain_text
        
        item = {
            'id': item_id,
            'title': title,
            'content': plain_text,
            'snippet': snippet,
            'node_type': 'note',
            'keywords': keywords,
            'source_file': filename,
            'raw_content': content,  # Keep original markdown
            'created_at': datetime.now()
        }
        
        logger.info(f"Processed markdown file: {filename} -> {title}")
        return [item]
    
    def _process_pdf_file(self, pdf_file: Dict) -> List[Dict]:
        """
        Extract structured data from a PDF file
        
        Args:
            pdf_file: Dict with 'filename' and 'content' keys (content as bytes)
            
        Returns:
            List of processed items from the PDF file
        """
        filename = pdf_file['filename']
        content_bytes = pdf_file['content']
        
        # Extract text from PDF
        extracted_text = self._extract_text_from_pdf(content_bytes)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            logger.warning(f"Could not extract meaningful text from PDF: {filename}")
            return []
        
        # Generate unique ID based on filename and content hash
        content_hash = hashlib.md5(content_bytes).hexdigest()[:8]
        item_id = f"pdf_{filename}_{content_hash}"
        
        # Extract title (try to get from first line or use filename)
        title = self._extract_title_from_pdf(extracted_text) or filename.replace('.pdf', '')
        
        # Extract keywords and key phrases
        keywords = self._extract_keywords(extracted_text)
        
        # Create snippet (first 300 chars of content)
        snippet = extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
        
        item = {
            'id': item_id,
            'title': title,
            'content': extracted_text,
            'snippet': snippet,
            'node_type': 'pdf',
            'keywords': keywords,
            'source_file': filename,
            'created_at': datetime.now()
        }
        
        logger.info(f"Processed PDF file: {filename} -> {title} ({len(extracted_text)} chars)")
        return [item]
    
    def _process_links_data(self, links_data: Any) -> List[Dict]:
        """
        Process saved links from JSON or CSV format
        
        Args:
            links_data: JSON object or CSV string containing links
            
        Returns:
            List of processed link items
        """
        processed_links = []
        
        try:
            # Handle JSON format
            if isinstance(links_data, (dict, list)):
                links_list = links_data if isinstance(links_data, list) else [links_data]
                
                for i, link in enumerate(links_list):
                    processed_link = self._process_single_link(link, i)
                    if processed_link:
                        processed_links.append(processed_link)
            
            # Handle CSV format
            elif isinstance(links_data, str):
                csv_reader = csv.DictReader(StringIO(links_data))
                for i, row in enumerate(csv_reader):
                    processed_link = self._process_single_link(row, i)
                    if processed_link:
                        processed_links.append(processed_link)
                        
        except Exception as e:
            logger.error(f"Error processing links data: {e}")
            
        logger.info(f"Processed {len(processed_links)} links")
        return processed_links
    
    def _process_single_link(self, link_data: Dict, index: int) -> Optional[Dict]:
        """
        Process a single link entry
        
        Args:
            link_data: Dictionary containing link information
            index: Index for ID generation
            
        Returns:
            Processed link item or None if invalid
        """
        # Try to extract URL from various possible field names
        url = (link_data.get('url') or 
               link_data.get('link') or 
               link_data.get('href') or 
               link_data.get('URL'))
        
        if not url:
            logger.warning(f"No URL found in link data: {link_data}")
            return None
        
        # Extract title from various possible field names
        title = (link_data.get('title') or 
                link_data.get('name') or 
                link_data.get('description') or 
                url.split('/')[-1] or 
                f"Link {index + 1}")
        
        # Extract description/content
        description = (link_data.get('description') or 
                      link_data.get('notes') or 
                      link_data.get('content') or 
                      "")
        
        # Extract tags/keywords
        tags = link_data.get('tags', [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',')]
        
        # Generate keywords from title and description
        keywords = self._extract_keywords(f"{title} {description}")
        keywords.extend(tags)
        keywords = list(set(keywords))  # Remove duplicates
        
        # Generate unique ID
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        item_id = f"link_{url_hash}"
        
        # Create snippet
        content_text = f"{title}. {description}".strip()
        snippet = content_text[:200] + "..." if len(content_text) > 200 else content_text
        
        item = {
            'id': item_id,
            'title': title,
            'content': content_text,
            'snippet': snippet,
            'node_type': 'link',
            'keywords': keywords,
            'url': url,
            'description': description,
            'tags': tags,
            'created_at': datetime.now()
        }
        
        return item
    
    def _extract_title_from_markdown(self, content: str) -> Optional[str]:
        """Extract the first heading from markdown content"""
        # Look for # heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()
        
        # Look for === or --- underlined headings
        underline_match = re.search(r'^(.+)\n[=\-]+$', content, re.MULTILINE)
        if underline_match:
            return underline_match.group(1).strip()
        
        return None
    
    def _markdown_to_text(self, md_content: str) -> str:
        """Convert markdown to plain text"""
        try:
            # Use markdown library to convert to HTML, then strip tags
            html = markdown.markdown(md_content)
            # Simple tag removal (for basic HTML)
            text = re.sub(r'<[^>]+>', '', html)
            # Clean up extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        except Exception:
            # Fallback: simple markdown removal
            text = re.sub(r'[#*`_\[\]()]+', '', md_content)
            return re.sub(r'\s+', ' ', text).strip()
    
    def _extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract keywords from text using simple heuristics
        
        Args:
            text: Input text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of extracted keywords
        """
        if not text:
            return []
        
        # Convert to lowercase and remove special characters
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = clean_text.split()
        
        # Filter out common stop words and short words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter and count words
        word_freq = {}
        for word in words:
            if (len(word) > 2 and 
                word not in stop_words and 
                not word.isdigit()):
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    def _extract_text_from_pdf(self, content_bytes: bytes) -> str:
        """
        Extract text from PDF using multiple methods for best results
        
        Args:
            content_bytes: PDF file content as bytes
            
        Returns:
            Extracted text string
        """
        extracted_text = ""
        
        try:
            # Method 1: Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(BytesIO(content_bytes)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    logger.debug(f"Extracted {len(extracted_text)} chars using pdfplumber")
        
        except Exception as e:
            logger.debug(f"pdfplumber failed: {e}, trying PyPDF2...")
            
            try:
                # Method 2: Fallback to PyPDF2
                pdf_reader = PyPDF2.PdfReader(BytesIO(content_bytes))
                text_parts = []
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    logger.debug(f"Extracted {len(extracted_text)} chars using PyPDF2")
            
            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed: {e2}")
                return ""
        
        # Clean up the extracted text
        if extracted_text:
            # Remove excessive whitespace
            extracted_text = re.sub(r'\s+', ' ', extracted_text)
            # Remove common PDF artifacts
            extracted_text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', ' ', extracted_text)
            extracted_text = extracted_text.strip()
        
        return extracted_text
    
    def _extract_title_from_pdf(self, text: str) -> Optional[str]:
        """
        Extract title from PDF text content
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Extracted title or None
        """
        if not text:
            return None
        
        # Split into lines and look for a title-like first line
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Check first few lines for title-like content
        for line in lines[:5]:
            # Skip very short lines or lines that look like headers/footers
            if len(line) > 5 and len(line) < 100:
                # Skip lines that are all caps (likely headers)
                if not line.isupper():
                    # Skip lines with lots of numbers (likely page numbers, dates)
                    if len(re.findall(r'\d', line)) < len(line) * 0.3:
                        return line
        
        # Fallback: use first substantial line
        for line in lines:
            if len(line) > 10 and len(line) < 150:
                return line[:100]  # Truncate if too long
        
        return None
