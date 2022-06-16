

def transform_list_object(li):
    dic = {}
    for item in li:
        id = int(item['id'])
        dic.update({id: item})
    # print(dic)
    return dic