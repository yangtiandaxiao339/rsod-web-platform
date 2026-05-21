import request from "../utils/request";

export const getModelList = () =>
  request({
    url: "/model/list",
    method: "get",
  });

export const getCurrentModel = () =>
  request({
    url: "/model/current",
    method: "get",
  });

export const reloadModel = (data) =>
  request({
    url: "/model/reload",
    method: "post",
    data,
  });
