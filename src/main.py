from src.log import logger
from src.config import CONFIG, GEMINI_API_KEY
import os
from pathlib import Path
from src.vectorDB import MultimodalVectorStore
from src.load_pdf import process_pdf
from src.generate_response import generate_gemini_response

def main(user_query):
    # 1. Prepare environment and load documents
    os.makedirs(CONFIG["data_dir"], exist_ok=True)
    os.makedirs(CONFIG["vector_store_dir"], exist_ok=True)

    pdf_paths = [Path(CONFIG["data_dir"]) / f for f in os.listdir(CONFIG["data_dir"]) if f.endswith(".pdf")]

    if not pdf_paths:
        logger.error(f"No PDF files found in {CONFIG['data_dir']}. Please upload your research papers.")
        return

    # 2. Process PDFs and populate vector store
    vector_store = MultimodalVectorStore(CONFIG["embedding_model"])

    for pdf_path in pdf_paths:
        text_docs, image_docs = process_pdf(pdf_path)
        vector_store.add_documents(text_docs)
        vector_store.add_documents(image_docs)

    # 3. Handle a user query
    

    # 4. Retrieve relevant context
    retrieved_text, retrieved_images = vector_store.retrieve(
        user_query,
        top_k_text=CONFIG["top_k_text"],
        top_k_images=CONFIG["top_k_images"]
    )

    # 5. Build the multimodal prompt for the Gemini API
    # Create the text context string
    text_context = "\n\n".join([f"Text from page {doc['metadata']['page']}: {doc['content']}" for doc in retrieved_text])

    # Extract image data and create descriptions
    images_data = [img["content"] for img in retrieved_images]
    image_descriptions = "\n".join([f"Figure {img['metadata']['figure_num']} (page {img['metadata']['page']}): {img['metadata']['caption']}" for img in retrieved_images])

    llm_prompt = f"""
    You are an expert research assistant. Based on the provided text and images, answer the user's query comprehensively.

    ### Provided Text Context:
    {text_context}

    ### Provided Image Context:
    The following images are provided, with their corresponding captions below:
    {image_descriptions}

    ### User Query:
    {user_query}

    ### Final Answer:
    """

    # 6. Call the Gemini API and print the final response
    logger.info("Sending prompt and images to Gemini API...")
    final_response = generate_gemini_response(llm_prompt, images_data)

    logger.info("--- Final Generated Response ---")
    print(final_response)
    logger.info("----------------------------------")
    return final_response

# if __name__ == "__main__":
#     user_query = input("Enter a query: ")
#     main(user_query)
