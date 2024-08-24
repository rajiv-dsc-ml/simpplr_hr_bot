from custom_pdf_parser import CustomDocumentLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import time
from dotenv import load_dotenv
import os

load_dotenv()
# initialize connection to pinecone (get API key at app.pinecone.io)
api_key = os.getenv("PINECONE_API_KEY")

# configure client
pc = Pinecone(api_key=api_key)

index_name = "simpplr-hr-assistant"
# intialise your pinecone vector database with the index_name
# check if vdb with index name already exists (it shouldn't if this is first time)
if index_name not in pc.list_indexes().names():
  # if does not exist, create index
  pc.create_index(
      name=index_name,
      dimension=1536, # model dimension
      metric="cosine", # similarity metric , can also be dot-product
      spec=ServerlessSpec(
          cloud="aws",
          region="us-east-1"
      )
  )
    # wait for index to be initialized
  while not pc.describe_index(index_name).status['ready']:
      time.sleep(1)

# connect to index
index = pc.Index(index_name)
time.sleep(1)


print(f" index has {index.describe_index_stats()['total_vector_count']} chunk-vectors")
# view index stats

# suppose all these documents were part of same pdf and not different pdfs.
# It will be a book of all the HR policies where each pdf is a chapter in this book.
# the final thing we need is only the page_content to run markdown_splitter.split_text(
heading3_heading2_pattern1 = (r'\n\n\d{1,2}\.\d{1,2}', r'\n\n\d{1,2}\.')
heading3_heading2_pattern2 = (r'\n\n\d\.\d([\w\s-]+):\n' , r'\n\n\d\.([\w\s-]+):\n')

pdf_to_pattern_map = {'GPT- POSH policy.pdf': heading3_heading2_pattern1,
 'GPT - grievance and disciplinary policy.pdf': heading3_heading2_pattern2,
 'GPT- ESOPS policy.pdf': heading3_heading2_pattern1,
 'GPT - Travel Reimbursement Policy.pdf': heading3_heading2_pattern1,
 'GPT- Remote Work Policy.pdf': heading3_heading2_pattern2,
 'GPT - Expense Reimbursement Policy.pdf': heading3_heading2_pattern1,
 'GPT- Recruitment and Onboarding Policy.pdf':heading3_heading2_pattern1,
 'GPT-parental leave policy.pdf': heading3_heading2_pattern2,
 'GPT - leave policy.pdf':heading3_heading2_pattern2,
 'GPT- Information security and IT policy..pdf':heading3_heading2_pattern1}
md_header_splits = None
if index.describe_index_stats()['total_vector_count'] == 0 :
  combined_policy_texts = ''
  combined_docs = []
  count = 0
  destination_folder = './DS Assignment/pdfs/'
  for i,each_pdf in enumerate(os.listdir(destination_folder) ):
    pdf_path = destination_folder + each_pdf
    print("file path -->",pdf_path)
    heading3_pat , heading2_pat = pdf_to_pattern_map.get(each_pdf , (r'\n\n\d{1,2}\.\d{1,2}', r'\n\n\d{1,2}\.'))
    print("here",heading3_pat , heading2_pat)
    loader = CustomDocumentLoader(pdf_path)
    documents = list(loader.lazy_load_remove_pattern(heading3_pat , heading2_pat))
    doc_text = ''.join([doc.page_content for doc in documents])
    count += 1
    combined_docs.append(doc_text)
    if combined_policy_texts != '':
      combined_policy_texts = combined_policy_texts + '\n' + doc_text
    else:
      combined_policy_texts = doc_text


  #
  print(len(os.listdir('/content/destination_folder/DS Assignment/pdfs')) == count)




  #text_splitter = SemanticChunker(OpenAIEmbeddings())
  #text_splitter2 = SemanticChunker(LlamaCppEmbeddings())

  headers_to_split_on = [
      ("#", "Header 1"),
      ("##", "Header 2"),
      ("###", "Header 3"),
  ]


  markdown_splitter = MarkdownHeaderTextSplitter(
      headers_to_split_on=headers_to_split_on
  )

  md_header_splits = markdown_splitter.split_text(combined_policy_texts)

  # cross-verification
  distinct_header1 = set()

  for doc in md_header_splits :
    distinct_header1.add(doc.metadata['Header 1'])

  assert len(distinct_header1) == len(os.listdir(destination_folder)), "the number of titles coming in splits is not equal to the number of pdfs. Debug !"

  # with higher dimensions like 1536, cosine similarity is generally the preferred metric. 
  # This is because cosine similarity focuses on the direction of the vectors, 
  # which is often more relevant for comparing the semantic meaning of text.



  # upserting 

embeddings = OpenAIEmbeddings()
print(f"{index.describe_index_stats()['total_vector_count'] == 0}")
if index.describe_index_stats()['total_vector_count'] == 0 :
  docsearch = PineconeVectorStore.from_documents(md_header_splits, embeddings, index_name=index_name)
else:
  docsearch = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)


def get_answer(query):

    documents = docsearch.similarity_search_with_score(query, k=3)
    print(documents)
    docs , scores = zip(*documents)
    print(scores)
    clubbed_docs = list(zip([doc.page_content for doc in docs], scores))
    if max(scores) < 0.73 :
      return "your question is irrelevant", 
    # make context by joining top 3 similar documents
    
    context = "\n".join([doc.page_content for doc in docs])

    try:
      model = OpenAI(model_name="gpt-3.5-turbo-instruct")
       

      # Use invoke() instead of __call__()
      response = model.invoke(f"Context: {context}\n\nQuestion: {query}\n\nAnswer:")
      #print(response)
      return response, clubbed_docs
    except Exception as e:
      raise RuntimeError(f"Error while generating the response: {str(e)}")