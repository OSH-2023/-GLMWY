import ray
import torch
import os
# from keybert import KeyBERT
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc


@ray.remote
def text_tagging(file_path, keywords_num=10):
    keywords_num=int(keywords_num)
    torch.cuda.is_available = lambda: False
    kw_model = KeyBERT(model='paraphrase-MiniLM-L6-v2')
    with open(file_path, "r") as f:
        text = f.read()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 1), top_n=keywords_num)
    return repr(list(keywords))

@ray.remote
def img_tagging(file_path, keywords_num=10):
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    # 设置Clarifai的API密钥
    api_key = 'bd56672a34a84a94a103b9847b2a28b2'
    application_id="MyGlow"
    # 验证
    metadata = (("authorization", f"Key {api_key}"),)
    request = service_pb2.PostModelOutputsRequest(
        model_id="general-image-recognition",
        user_app_id=resources_pb2.UserAppIDSet(app_id=application_id),
        inputs=[
            resources_pb2.Input(
                data=resources_pb2.Data(image=resources_pb2.Image(base64=file_bytes))
            )
        ],
    )
    stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())
    response = stub.PostModelOutputs(request, metadata=metadata)

    if response.status.code != status_code_pb2.SUCCESS:
        print(response)
        raise Exception(f"请求失败,状态码为: {response.status}")

    # for concept in response.outputs[0].data.concepts:
    #     print("%12s: %.2f" % (concept.name, concept.value))
    keywords=[]
    for concept in response.outputs[0].data.concepts[0:keywords_num]:
        keywords.append(str(concept.name))
    return repr(list(keywords))


def tagging(file_path):
    ray.init()
    print("开始打标")
    tagging_function_table={
        "txt":text_tagging,
        "jpg": img_tagging
    }
    temp=file_path
    _, filename = os.path.split(temp)
    file_ext=filename.split(".")[-1]
    # print("     ----Check:ext----:"+str(file_ext))
    # print("     ----Check:path----:"+str(file_path))
    tagging_function=tagging_function_table[file_ext]
    ID=tagging_function.remote(file_path)
    keywords=ray.get(ID)
    print("打标结束:"+str(keywords))
    return keywords

if __name__ == "__main__":
    # tagging("test.txt")
    tagging("cat.jpg")