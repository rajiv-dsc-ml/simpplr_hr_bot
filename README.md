# simpplr_hr_bot
The HR assistant that answers questions of employees about the company policies.

## Simple Problem Statement : Talk to your data 

## Problem Statement :
Given policy pdfs, build a QA system to answer policy questions with the help of these pdfs .

## The first idea : 
A chat based LLM is perfect system to converse and ask questions to obtain answers. However, the answers from a chatbot is limited in nature. It can answer only the questions based on the knowledge text it is trained on or if the answer to the question can be logically obtained from the text on which it is trained on .

The knowledge specific to a particular domain (in this case a specific company policies) is unlikely to be answered by such LLMs. RAG is a method to inject the specific knoweledge to the system . 
Using RAG we can enrich the prompt with the latest knowledge text that the LLM can further use to answer the relevant questions.

# Main libraries used 
1. tessaract : pypdf was performing bad to parse the pdf data to text , hence it was used
2. regex : to mark the headings and subheading using regex patterns
3. langchain : makes it easy to develop the rag based agentic system. It supports almost all the requirements while developing RAG system : reading data , chunking , retrival of chunks
4. pinecone : easy to use . Sorry , I should have used ES vector DB , but , to complete the assignment quickly, I focused more on data analysis part and reading data part

## Pros and cons of the problem at hand :
One pro is that the data is very structured. The pdfs are not noisy (unlike the pdfs that contain handwritten text) and is structured , i.e contains specific headings and subheadings denoting the nature of the information present in that pdf . 

Con : The pdfs are distinct and not part of one big company-specific pdf . It is not a very huge issue and can be mitigated conviniently.
Note that the pdfs are separated, but , after parsing the text , the whole text can be combined and be treated as a book with the titles of each pdf as its chapters.


## Major steps in developing RAG system 🇰
1. Parse the data or read the data
2. Chunking : split the data into chunks. The goal is that a chunk contains information related to a specific topic or subtopic. 
3. Conversion of chunks into vectors and upsert in a Vector database 
4. Retrival of chunks and enriching the prompt 

## Chunking is a very important step .
My choice of chunking is MarkdownHeaderTextSplitter
Why ? The nature of the data is such that the information is followed by a given heading and subheading .
This pair of a heading and a subheading or in some case a triplet of heading , subheading , sub-sub-heading can be used to chunk different parts of the pdf text belonging to particular topics. 

## Data Analysis : The most crucial part
All the pdf files were analysed to get the regex pattern to identify the heading , subheading2, subheading3
 heading is the title of the pdf 
 subheading2 is like 'Introduction' , 'Conclusion'
 subheading3 comes optional in some cases when the text under a subheading has further points of texts .
 Analysis showed me two different pair of patterns for subheading2 and subheading3 which were used as part of Custom Pdf Reader Class to mark the heading with # , subheading2 with '##'
and subheading3 with '###' 

 Note that heading is very easy to identify , as it is the title which is present in the first page of the pdf itself 
 subheading2 and subheading3 follow one of the 2 identified pairs of regex patterns
 Each pdf can belong to one of these two identified pairs 
 Hence a map is prepared that stores the pdf filepath as key and the pair of the regex patterns as the value that pdf file follows for the marking of subheading2 and subheading3


### Need for writing custom pdf parser 
I first experimented with usual pypdf on which a langchain wrapper is available .
But , it was erroneosly giving next line character (\n) after each few words . 

Writing custom pdf parser (Document Loader)  helps:
1. to read data properly from a given pdf
2. to mark every title with '#' using regex
3. to mark every subheading with '##' using regex
4. to mark every sub to subheading with '###' using regex

# Docker file and docker comppose yaml have been written 
# A similarity threshold has been set at 0.73 , below which the query is said to be irrelavant , like "What is Earth?". This method requires more testing to validate and there can be other approaches also to handle such cases like with the help of prompting , "If the query is irrelevant being asked to HR professional , then answer 'not relevant query'"

# The errors like intenet inavailaibility , wrong api key  have been handled or any untoward error while quring the llm are handled 
# Possible imporovements
I didnt go for these because , my test cases were giving good enough answers 
1. Enriching the page_content : We can make heading and subheading which are parts of metadata , parts of chunk text , so to make it more informative
