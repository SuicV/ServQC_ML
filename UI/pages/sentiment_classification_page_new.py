import imp
import streamlit as st
from Classifiers.NLPSentimentClassifier import NLPSentimentClassifier
import spacy
import pandas as pd
import plotly.express as px
from utils.coreference_graph import coreference_graph
from streamlit.components.v1 import html
from gensim.models import Word2Vec
from Aspects.CoRefAspectIdentGrouping import CoRefAspectIdentGrouping
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def plot_word_cloud(explicite_aspects):
	wc = WordCloud(background_color="white",width=800,height=500, relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(explicite_aspects)

	st.set_option('deprecation.showPyplotGlobalUse', False)
	plt.imshow(wc, interpolation='bilinear')
	plt.axis("off")
	plt.show()
	st.pyplot(width=800, height=500)
	plt.close()
	pass

def sentiment_classification_page():
	nlp = spacy.load("en_core_web_sm")

	with st.expander("Hotel aspects"):
		file = open('explicit_aspects.txt', 'r')
		explicite_aspects = eval(file.readline())
		file.close()
		plot_word_cloud(explicite_aspects)

	with st.expander("Simlar Aspects"):
		coref_aspects_ident_group = CoRefAspectIdentGrouping(pd.DataFrame([]), dict(explicite_aspects), nlp)
		coref_aspects_ident_group.model_wv = Word2Vec.load("100K_reviews_model_sg_hs_10.pkl")
		coref_groups = coref_aspects_ident_group.get_co_reference_aspects_groups(0.498)
		coreference_graph(coref_groups)
                
		htmlfile = open("coref_colors_guide.html", "r", encoding="utf-8")
		html(htmlfile.read(), height=50)
		htmlfile.close()

		htmlfile = open("temp_html.html", "r", encoding="utf-8")
		html(htmlfile.read(), width=1000, height=550)
		htmlfile.close()
	dataset_file = None
	with st.form("config_sentiment_classification"):
		dataset_file = st.file_uploader("Upload cleaned dataset", type = ["csv"])
		submited = st.form_submit_button("Classify")

	if submited and dataset_file is not None:
		nlp = spacy.load("en_core_web_sm")
		df = pd.read_csv(dataset_file, encoding="utf-8")
		df = df[df['cleaned_review'].notna()]
		st.write(df)
		
		nlp_classifier = NLPSentimentClassifier(df["cleaned_review"], list(explicite_aspects), nlp)
		
		classification_result = nlp_classifier.start()
		
		grouped_classification_result = classification_result.groupby(["aspect", "sentiment"]).size().reset_index(name="count").sort_values("count", ascending=False)
		sentiment_plot = px.bar(grouped_classification_result, x="aspect", y="count", color="sentiment", width=1000, height=500)

		aggregated_result = grouped_classification_result.groupby(["sentiment"]).sum("count").reset_index()
		pi_plot = px.pie(aggregated_result, names="sentiment", values="count")

		st.plotly_chart(sentiment_plot, use_container_width=True)
		st.plotly_chart(pi_plot)

	pass