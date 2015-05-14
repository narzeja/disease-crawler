==Abstract==

In this paper we design and construct models for assisting physicians
with the task of diagnosing rare diseases. Using a prior knowledge of
rare diseases consisting of 'disease name' and 'abstract',
we utilize the 'Google Search Engine' to harvest additional
knowledge of 3882 rare diseases to expand the model. Using various
techniques, ranging from data set noise reduction, to Machine
Learning and Natural Language Processing are applied in order to
construct different models and subsequently compare them in terms of
prediction precision.

Results: The most successful approach (Orphanet Abstracts+Noise Reduced googled
data with TFIDF modelling) places 86\% (37 out of 43) of the diseases
within the top 5 predicted results and 95\% (41 out of 43) within top
20. The model is based on harvested information and prior information
(abstracts from Orphanet), and is implemented using a basic 'Term
Frequency - Inverse Document Frequency' model.
