from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk
import ray

# nltk.download('stopwords')
# ray.init(address="auto", _redis_password='5241590000000000')

# @ray.remote
def text_tagging(file_path, keywords_num=10):
    # 读取文件
    with open(file_path, 'r') as f:
        text = f.read()
    # 将文本分词
    tokens = word_tokenize(text.lower())
    # 去除停用词
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    # 统计词频
    freq_dist = FreqDist(tokens)
    # 获取前N个出现频率最高的词作为关键词
    keywords = [token for token, freq in freq_dist.most_common(keywords_num)]
    return repr(keywords)

def tagging(file_path):
    print("开始打标")
    tagging_function_table={
        "txt":text_tagging

    }
    file_name=file_path.split("/")[-1]
    file_ext=file_name.split(".")[1]
    print("Check:ext:"+str(file_ext))
    print("Check:path:"+str(file_path))
    # tagging_function=tagging_function_table[file_ext]
    # ID = tagging_function.remote(str(file_path))
    # keywords = ray.get(ID)
    keywords=text_tagging(file_path)
    # print(keywords)
    print("打标结束:"+str(keywords))
    return keywords
