# -*- coding: utf-8 -*-

import datetime
import io
import traceback
import srt

#
# Text: This is a tragedy for Ukraine
# start_time: 55.0, end_time: 61.9
# Confidence: 1.0
# Time offset for the first frame: 55.0
# Rotated Bounding Box Vertices:
#         Vertex.x: 0.3453125059604645, Vertex.y: 0.8166666626930237
#         Vertex.x: 0.6539008021354675, Vertex.y: 0.8134080767631531
#         Vertex.x: 0.6540446877479553, Vertex.y: 0.8564628958702087
#         Vertex.x: 0.3454563617706299, Vertex.y: 0.8597214818000793


def make_new_sub(subs, text_annotation):
    text_segment = text_annotation.segments[0]
    start_time = text_segment.segment.start_time_offset
    end_time = text_segment.segment.end_time_offset
    sub = srt.Subtitle(index=len(subs),
                       start=datetime.timedelta(seconds=start_time.seconds,
                                                microseconds=start_time.microseconds),
                       end=datetime.timedelta(seconds=end_time.seconds, microseconds=end_time.microseconds),
                       content=text_annotation.text)
    subs.append(sub)
    return subs

def get_vertex_y_0(text_segment):
    # Show the result for the first frame in this segment.
    frame = text_segment.frames[0]
    return frame.rotated_bounding_box.vertices[0].y

def make_sentences(subs, text_annotation, old_text_annotation):
    # Get the first text segment
    # 位置偏，显示时间小于1s，均不要
    # 不应该只取第0个段落，应该foreach一下
    idx_cur = len(subs)
    idx_pre = idx_cur - 1
    text_segment = text_annotation.segments[0]
    start_time = text_segment.segment.start_time_offset
    end_time = text_segment.segment.end_time_offset
    vertex_y_0_cur = get_vertex_y_0(text_segment)

    # Hava pre one, maybe need 'return /n' line
    if old_text_annotation is not None:
        pre_text_segment = old_text_annotation.segments[0]
        pre_start_time = pre_text_segment.segment.start_time_offset
        vertex_y_0_pre = get_vertex_y_0(pre_text_segment)
        # old and new is same && y is diff
        if start_time.seconds == pre_start_time.seconds:
            sub_pre = subs[idx_pre]
            text = sub_pre.content
            if vertex_y_0_cur > vertex_y_0_pre:
                text = sub_pre.content + " " + text_annotation.text
            else:
                text = text_annotation.text + " " + sub_pre.content
            sub_pre.content = text
        else:
            subs = make_new_sub(subs, text_annotation)
    else:
        subs = make_new_sub(subs, text_annotation)
    return subs

def check_sub(text_annotation):
    # 如果没有空格，则不是
    text = text_annotation.text
    # if text.find(" ") == -1:
    #     print("英文无空格，非字幕")
    #     return False

    if len(text) < 5:
        print("英文长度小于5，非字幕")
        return False

    text_segment = text_annotation.segments[0]
    start_time = text_segment.segment.start_time_offset
    end_time = text_segment.segment.end_time_offset
    frame = text_segment.frames[0]
    if frame.rotated_bounding_box.vertices[0].y < 0.7:
        print("位置不正确")
        return False

    if end_time.seconds - start_time.seconds < 0.2:
        print("时间太短<0.2s")
        return False

    return True

# 获取列表的第二个元素
def take_start_time(text_annotation):
    start_time = text_annotation.segments[0].segment.start_time_offset
    return start_time.seconds

def detect_text(path):
    """Detect text in a local video."""
    from google.cloud import videointelligence

    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.TEXT_DETECTION]
    video_context = videointelligence.VideoContext()

    with io.open(path, "rb") as file:
        input_content = file.read()

    operation = video_client.annotate_video(
        request={
            "features": features,
            "input_content": input_content,
            "video_context": video_context,
        }
    )

    print("\nProcessing video for text detection.")
    result = operation.result(timeout=300)

    # The first result is retrieved because a single video was processed.
    annotation_result = result.annotation_results[0]

    subs = []
    index = 0
    vertex_y_list = []
    dis_duration = []
    # 处理了每一句话

    # 排序
    annotation_result.text_annotations.sort(key=take_start_time)

    old_text_annotation = None
    for text_annotation in annotation_result.text_annotations:
        print("\nText: {}".format(text_annotation.text))
        is_sub = check_sub(text_annotation)
        if is_sub is not True:
            continue
        # Get the first text segment
        text_segment = text_annotation.segments[0]
        start_time = text_segment.segment.start_time_offset
        end_time = text_segment.segment.end_time_offset
        print(
            "start_time: {}, end_time: {}".format(
                start_time.seconds + start_time.microseconds * 1e-6,
                end_time.seconds + end_time.microseconds * 1e-6,
            )
        )

        print("Confidence: {}".format(text_segment.confidence))

        # Show the result for the first frame in this segment.
        frame = text_segment.frames[0]
        time_offset = frame.time_offset
        print(
            "Time offset for the first frame: {}".format(
                time_offset.seconds + time_offset.microseconds * 1e-6
            )
        )
        print("Rotated Bounding Box Vertices:")
        for vertex in frame.rotated_bounding_box.vertices:
            print("\tVertex.x: {}, Vertex.y: {}".format(vertex.x, vertex.y))
            vertex_y_list.append(vertex.y)
        dis_duration.append(end_time.seconds - start_time.seconds)
        subs = make_sentences(subs, text_annotation, old_text_annotation)
        old_text_annotation = text_annotation
    try:
        # vertex_y_avg = sum(vertex_y_list) / float(len(vertex_y_list))
        # dis_duration_avg = sum(dis_duration) / float(len(dis_duration))
        # print('vertex_y_avg: ' + str(vertex_y_avg) + " dis_duration: " + str(dis_duration_avg))
        # sql.update_vi_args(jobid, str(dis_duration_avg), str(vertex_y_avg))
        pass
        # [0]---------[1]
        #  |           |
        #  |           |
        # [3]---------[4]
        # handle2(annotation_result, vertex_y_avg, dis_duration_avg)
    except Exception as e:
        print(e)
        print(traceback.format_exc())

    ret = None
    if len(subs) > 0:
        ret = srt.compose(subs)
        print(ret)
    return ret

def detect_text_uri(input_uri):
    """Detect text in a video stored on GCS."""
    from google.cloud import videointelligence

    video_client = videointelligence.VideoIntelligenceServiceClient()
    features = [videointelligence.Feature.TEXT_DETECTION]

    operation = video_client.annotate_video(
        request={"features": features, "input_uri": input_uri}
    )

    print("\nProcessing video for text detection.")
    result = operation.result(timeout=600)

    # The first result is retrieved because a single video was processed.
    annotation_result = result.annotation_results[0]

    for text_annotation in annotation_result.text_annotations:
        print("\nText: {}".format(text_annotation.text))

        # Get the first text segment
        text_segment = text_annotation.segments[0]
        start_time = text_segment.segment.start_time_offset
        end_time = text_segment.segment.end_time_offset
        print(
            "start_time: {}, end_time: {}".format(
                start_time.seconds + start_time.microseconds * 1e-6,
                end_time.seconds + end_time.microseconds * 1e-6,
            )
        )

        print("Confidence: {}".format(text_segment.confidence))

        # Show the result for the first frame in this segment.
        frame = text_segment.frames[0]
        time_offset = frame.time_offset
        print(
            "Time offset for the first frame: {}".format(
                time_offset.seconds + time_offset.microseconds * 1e-6
            )
        )
        print("Rotated Bounding Box Vertices:")
        for vertex in frame.rotated_bounding_box.vertices:
            print("\tVertex.x: {}, Vertex.y: {}".format(vertex.x, vertex.y))

def asr_mp4(input_mp4):
    """
    Transcribe long audio file from Cloud Storage using asynchronous speech
    recognition

    Args:
      input_mp4: file path
    """
    ret = None
    try:
        ret = detect_text(input_mp4)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return ret