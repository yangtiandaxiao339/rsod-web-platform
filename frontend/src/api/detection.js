import request from "../utils/request";

export const detectSingleImage = (data) =>
  request({
    url: "/detection/single",
    method: "post",
    data,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const getDetectionHistory = (params) =>
  request({
    url: "/detection/history",
    method: "get",
    params,
  });

export const getDetectionDetail = (id) =>
  request({
    url: `/detection/detail/${id}`,
    method: "get",
  });

export const getTargetList = () =>
  request({
    url: "/detection/targets/list",
    method: "get",
  });
