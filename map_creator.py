# 匯入模組
import json
import math


# 處理座標成四方位
"""
def four_pos(ref_p, comp_p):
    '''
    回傳比較點相對於基準點較接近的四方位
    輸入:
    ref_p:基準點,(x,y)
    comp_p:比較點,(x,y)
    輸出:
    pos:方位，N/S/E/W
    '''
    x, y = comp_p[0] - ref_p[0], comp_p[1] - ref_p[1]  # xy座標標準化(使ref_p成為原點)
    if y >= (math.sqrt(2) + 1) * x and y >= (-math.sqrt(2) - 1) * x:
        return 'N'
    elif y <= (math.sqrt(2) + 1) * x and y <= (-math.sqrt(2) - 1) * x:
        return 'S'
    elif y >= (-math.sqrt(2) + 1) * x and y <= (math.sqrt(2) - 1) * x:
        return 'E'
    elif y >= (math.sqrt(2) - 1) * x and y <= (-math.sqrt(2) + 1) * x:
        return 'W'
"""
def four_pos(ref_p, comp_p):
    '''
    回傳比較點相對於基準點較接近的四方位(10度)
    輸入:
    ref_p:基準點,(x,y)
    comp_p:比較點,(x,y)
    輸出:
    pos:方位，N/S/E/W
    '''
    #度數->斜率
    #10->0.1763269807085
    #80->5.6712818196177
    x, y = comp_p[0] - ref_p[0], comp_p[1] - ref_p[1]  # xy座標標準化(使ref_p成為原點)
    if y >= -5.6712818196177 * x and y >= 5.6712818196177 * x:
        return 'N'
    elif y <= -5.6712818196177 * x and y <= 5.6712818196177 * x:
        return 'S'
    elif y >= -0.1763269807085 * x and y <= 0.1763269807085 * x:
        return 'E'
    elif y >= 0.1763269807085 * x and y <= -0.1763269807085 * x:
        return 'W'
    
#方位判斷
def judge_pos(ref_p, comp_p):
    """
    回傳比較點相對於基準點所在的方位
    輸入:
    ref_p:基準點,(x,y)
    comp_p:比較點,(x,y)
    輸出:
    pos:方位，NE/NW/SE/SW N/S/E/W None
    """
    if ref_p[1] > comp_p[1]:
        ret = 'S'
    elif ref_p[1] < comp_p[1]:
        ret = 'N'
    elif ref_p[1] == comp_p[1]:
        ret = ''

    if ref_p[0] > comp_p[0]:
        ret += 'W'
    elif ref_p[0] < comp_p[0]:
        ret += 'E'
    
    if ret=='':
        ret = None

    return ret


def generate_map(data):
    
    # 輸/讀入資料
    dot_data = json.loads(data)

    # 製作地圖格式檔案
    # dot_data = [[line_id, color, [[station_id, name, [[type, trans_sta], ... ], x, y]]]]
    # line_data = [[line_id, color, [x1, y1, x2, y2], ...]]
    line_data = []
    dot_pos_dict = {}
    for i in dot_data:
        for j in i[2]:
            dot_pos_dict[j[0]] = [j[3], j[4]]  # dot_pos_dict[station_id] = [x, y]

    # 清除舊檔案的所有座標資料
    for i in range(len(dot_data)):
        for j in range(len(dot_data[i][2])):
            dot_data[i][2][j][3] = None  # 清掉x
            dot_data[i][2][j][4] = None  # 清掉y

    # 找出轉乘站和端點站
    transfer_dict = {}
    for i in range(len(dot_data)):
        for j in range(len(dot_data[i][2])):
            if len(dot_data[i][2][j][2]) != 0:
                transfer_dict[dot_data[i][2][j][0]] = [i, j]
            if j==0 or j==len(dot_data[i][2])-1:
                transfer_dict[dot_data[i][2][j][0]] = [i, j]
    transfer_list = list(transfer_dict.keys())

    # 建立所有轉乘、(終點站)的字典與清單
    fixed_dict_copy = transfer_dict.copy()
    ##for i in range(len(dot_data)):
    ##    fixed_dict_copy[dot_data[i][2][0][0]] = [i, 0]
    ##    fixed_dict_copy[dot_data[i][2][len(dot_data)][0]] = [i, len(dot_data[i])]

    fixed_list_copy = list(fixed_dict_copy.keys())

    # 將轉乘及(終點站)的座標重新寫入
    min_pos = [999, 999]
    for i in range(len(fixed_list_copy)):
        station_id = fixed_list_copy[i]
        a, b = fixed_dict_copy[station_id]
        [x, y] = dot_pos_dict[station_id]
        if x < min_pos[0]:
            min_pos[0] = x
        if y < min_pos[1]:
            min_pos[1] = y
        dot_data[a][2][b][3], dot_data[a][2][b][4] = x, y
        
    # 調整座標

    for i in range(len(dot_data)):
        for j in range(len(dot_data[i][2])):
            try:
                dot_data[i][2][j][3] = round(dot_data[i][2][j][3] - min_pos[0],
                                             12)  # x
                dot_data[i][2][j][4] = round(dot_data[i][2][j][4] - min_pos[1],
                                             12)  # y

            except TypeError:
                continue



    # 將歪調直
    for i in range(len(dot_data)):
        trans_pos = None
        for j in range(len(dot_data[i][2])):
            if dot_data[i][2][j][3] == None:
                continue
            elif trans_pos == None:
                trans_pos = dot_data[i][2][j][3], dot_data[i][2][j][4]

            else:
                pos = four_pos(trans_pos,
                               [dot_data[i][2][j][3], dot_data[i][2][j][4]])
                if pos == 'N' or pos == 'S':
                    dot_data[i][2][j][3] = trans_pos[0]
                    for k in dot_data[i][2][j][2]:
                        [temp_i, temp_j] = transfer_dict[k[1]]
                        if k[0]=='in':
                            dot_data[temp_i][2][temp_j][3] = trans_pos[0]
                elif pos == 'E' or pos == 'W':
                    dot_data[i][2][j][4] = trans_pos[1]
                    for k in dot_data[i][2][j][2]:
                        [temp_i, temp_j] = transfer_dict[k[1]]
                        if k[0]=='in':
                            dot_data[temp_i][2][temp_j][4] = trans_pos[1]
                trans_pos = [dot_data[i][2][j][3], dot_data[i][2][j][4]]


    ##縮小站距差距


    # 處理普通站及路線
    # dot_data = [[line_id, color, [[station_id, name, [[type, trans_sta], ... ], x, y]]]]
    for i in range(len(dot_data)):
        style = ''
        section = []  # (車站代碼, j)
        for j in range(len(dot_data[i][2])):

            if j==0:  # 第1站
                section.append((dot_data[i][2][j][0], j))

            elif j==len(dot_data[i][2])-1:  # 最後1站
                if style=='':
                    style = 'single' #單段
                section.append((dot_data[i][2][j][0], j))

            elif len(dot_data[i][2][j][2])!=0:  # 如果(非首尾兩站)且是轉乘站
                if style=='':
                    style = 'multi'  # 多段
                section.append((dot_data[i][2][j][0], j))


        line_index = 0
        # line_data = [[line_id, color, [x1, y1, x2, y2], ...]...]
        for j in range(len(section)-1):
            if style=='single':
                if len(dot_data[i][2][section[j][1]][2])!=0 and len(dot_data[i][2][section[j+1][1]][2])!=0:  # 首尾站為轉乘站
                    pass
                    # 找出中點
                    middle_dot = ( (dot_data[i][2][section[j+1][1]][3]+dot_data[i][2][section[j][1]][3])/2 , (dot_data[i][2][section[j+1][1]][4]+dot_data[i][2][section[j][1]][4])/2 )
                    # 向兩端延伸
                    # 向前判斷 右上 右下 左上 左下
                    pos = judge_pos( middle_dot , (dot_data[i][2][section[j][1]][3], dot_data[i][2][section[j][1]][4]) )
                    if pos == None:
                        print('DATA ERROR!')

                    elif pos == 'N' or pos == 'S' or pos == 'E' or pos == 'W':
                        line_index += 1
                        line_id = dot_data[i][0] + str(line_index)
                        line_color = dot_data[i][1]
                        coord_1 = ( dot_data[i][2][section[j][1]][3], dot_data[i][2][section[j][1]][4] )
                        coord_2 = ( dot_data[i][2][section[j+1][1]][3], dot_data[i][2][section[j+1][1]][4] )
                        line_data.append( [line_id, line_color, [coord_1[0], coord_1[1], coord_2[0], coord_2[1]] ] )

                    else:
                        delta_x = (dot_data[i][2][section[j][1]][3] - middle_dot[0])
                        delta_y = (dot_data[i][2][section[j][1]][4] - middle_dot[1])

                        # 延伸
                        if math.abs(delta_x) < math.abs(delta_y):

                            if pos[0] == 'N':
                                front_pos = (dot_data[i][2][section[j][1]][3], middle_dot[1] + delta_x)
                                back_pos = (dot_data[i][2][section[j+1][1]][3], middle_dot[1] - delta_x)

                            elif pos[0] == 'S':
                                front_pos = (dot_data[i][2][section[j][1]][3], middle_dot[1] - delta_x)
                                back_pos = (dot_data[i][2][section[j+1][1]][3], middle_dot[1] + delta_x)


                        elif math.abs(delta_x) > math.abs(delta_y):
                            if pos[0] == 'E':
                                front_pos = ( middle_dot + delta_y , dot_data[i][2][section[j][1]][4])
                                back_pos = ( middle_dot - delta_y , dot_data[i][2][section[j+1][1]][4])

                            elif pos[0] == 'W':
                                front_pos = ( middle_dot - delta_y , dot_data[i][2][section[j][1]][4])
                                back_pos = ( middle_dot + delta_y , dot_data[i][2][section[j+1][1]][4])

                        line_index += 1
                        line_id = dot_data[i][0] + str(line_index)
                        line_color = dot_data[i][1]
                        coord_1 = ( dot_data[i][2][section[j][1]][3], dot_data[i][2][section[j][1]][4] )
                        coord_2 = ( dot_data[i][2][section[j+1][1]][3], dot_data[i][2][section[j+1][1]][4] )
                        line_data.append( [line_id, line_color, [coord_1[0], coord_1[1], front_pos[0], front_pos[1]]] )

                        line_index += 1
                        line_id = dot_data[i][0] + str(line_index)
                        line_data.append( [line_id, line_color, [front_pos[0], front_pos[1], back_pos[0], back_pos[1]]] )

                        line_index += 1
                        line_id = dot_data[i][0] + str(line_index)
                        line_data.append( [line_id, line_color, [back_pos[0], back_pos[1], coord_2[0], coord_2[1]]] )




                    # 向後延伸
                    # 判斷 右上 右下 左上 左下

                    # 4點都找出來了
                    # 加入line_data

                elif len(dot_data[i][2][section[j][1]][2])!=0:  # 首站為轉乘
                    pass
                    # 從尾站向前端延伸
                    # 4點都找出來了
                    # 加入line_data

                elif len(dot_data[i][2][section[j+1][1]][2])!=0:  # 尾站為轉乘
                    pass
                    # 從首站向後端延伸
                    # 4點都找出來了
                    # 加入line_data

                else:  # 首尾皆非轉乘
                    pass
                    # 找出中點
                    # 向兩端延伸
                    # 4點都找出來了
                    # 加入line_data

            elif style=='multi':
                if j==0:  # 是首站
                    pass

                else:  # 非首站
                    pass





    # 衝突分解(待方法產出)

    

    # 印出畫圖的HTML文件內容
    # 畫出線
    # line_data = [[line_id, color, [x1, y1, x2, y2], ...]]
    # line_data = [['A', '#0070BC', [0.02, 0.14, 0.12, 0.14]], ['B', '#0070BC', [0.12, 0.14, 0.14, 0.12]]]
    draw = """"""
    n = 5000
    for i in line_data:
        color = i[1]
        draw += f"""ctx.beginPath();
                    ctx.arc({i[2][0]*n}, {1200-(i[2][1]*n)}, 2.5, 0, 2 * Math.PI);
                    ctx.lineWidth = 5;
                    ctx.strokeStyle = '{color}';
                    ctx.stroke();

                    ctx.beginPath();
                    ctx.moveTo({i[2][0]*n}, {1200-(i[2][1]*n)});
                    ctx.lineTo({i[2][2]*n}, {1200-(i[2][3]*n)});
                    ctx.lineWidth = 10;
                    ctx.strokeStyle = '{color}';
                    ctx.stroke();
                    """

        if i == line_data[len(line_data)-1]:
            draw += f"""ctx.beginPath();
                        ctx.arc({i[2][0]*n}, {1200-(i[2][1]*n)}, 2.5, 0, 2 * Math.PI);
                        ctx.lineWidth = 5;
                        ctx.strokeStyle = '{color}';
                        ctx.stroke();
                        """



    # 畫出站
    multiline = [] #已經畫過的轉乘站
    multiline_progress = [] #已經畫過的轉乘站進度  #[id(first time), part(so far), all part] ex['A01', 2, 5]=>已經畫了2/5圓

    color = ''
    for i in dot_data:
        color = i[1]
        for j in i[2]:
            if j[3]==None or j[4]==None:
                continue

            isout = True
            for k in j[2]:
                if k[0]=='in':
                    isout = False
                    break

            if len(j[2])>0 and isout==False: #是轉乘站
                have_circle = None
                for k in j[2]:
                    if k[1] in multiline: #轉乘站已經被處理過
                        have_circle = k[1]
                        break
                if have_circle!=None: #轉乘站被處理過，要接著畫
                    for k in range(len(multiline_progress)):
                        if multiline_progress[k][0]==have_circle:
                            temp_data = multiline_progress[k]
                            part_so_far = temp_data[1]
                            all_part = temp_data[2]
                            temp_data[1] += 1
                            break

                else: #轉乘站沒被處理過，要加入清單中
                    multiline.append(j[0])
                    part_so_far = 0
                    all_part = len(j[2])+1
                    for k in j[2]:
                        if k[0]!='in':
                            all_part -= 1
                    multiline_progress.append( [j[0], 1, all_part] )


                draw += f"""
                        ctx.beginPath();
                        ctx.arc({j[3]*n+10}, {1200-(j[4]*n+10)}, 5,  (2 * Math.PI)/{all_part}*{part_so_far}+(0.5 * Math.PI), (2 * Math.PI)/{all_part}*{part_so_far + 1}+(0.5 * Math.PI) , true);
                        ctx.lineWidth = 10;
                        ctx.strokeStyle = '{color}';
                        ctx.stroke();
                        """

            else: #不是轉乘站

                '''
                draw += f"""
                        ctx.beginPath();
                        ctx.moveTo({j[3]*n}, {1200-(j[4]*n)});
                        ctx.lineTo({j[3]*n}, {1200-(j[4]*n+7)});
                        ctx.lineWidth = 7;
                        ctx.strokeStyle = '{color}';
                        ctx.stroke();
                        """
                '''
                draw += f"""
                        ctx.beginPath();
                        ctx.arc({j[3]*n+10}, {1200-(j[4]*n+10)}, 5, 0, 2 * Math.PI);
                        ctx.lineWidth = 10;
                        ctx.strokeStyle = '{color}';
                        ctx.stroke();
                        """

    """
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width">
        <title>拓樸地圖</title>
        <link href="style.css" rel="stylesheet" type="text/css" />
    </head>

    <body onload="draw();">

        <canvas id="canva" width="1200" height="1200">
        </canvas>

        <script>
            function draw() \u007B
                var canvas = document.getElementById('canva');
                if (canvas.getContext) \u007B
                    var ctx = canvas.getContext('2d');


                    {draw}
                \u007D
            \u007D
        </script>
    </body>

    </html>
    """
    
    document_HTML = f"""
        <canvas id="canva" width="1200" height="1200">
        </canvas>

        <script>
            function draw() \u007B
                var canvas = document.getElementById('canva');
                if (canvas.getContext) \u007B
                    var ctx = canvas.getContext('2d');


                    {draw}
                \u007D
            \u007D
            
            draw();
        </script>
    """
    
    return document_HTML






    # 排斥勒?(不用)

    # 拉回單飛的一站

    # 處理重疊的路線

    # 畫出路線圖並顯示

    # 最小化

    # 輸出最小化路線圖


