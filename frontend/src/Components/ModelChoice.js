import React from "react";
import axios from "axios";
import { useState, useEffect, useRef } from "react";

export default function ModelChoice(props) {
  let input = useRef();

  useEffect(() => {
    if (props.visible) {
      props.setTitle("How do you want to initialise the model?");
    }
  }, [props.visible]);

  let init_model_on_seed = () => {
    props.setLoading(true);
    axios
      .put(
        "http://127.0.0.1:5000/api/init_model",
        {},
        {
          headers: {
            "Access-Control-Allow-Origin": "*",
          },
        }
      )
      .then(() => {
        props.setLoading(false);
        props.setModelInitialised(true);
      })
      .catch((err) => console.log(err));
  };

  let load_model_from_file = () => {
    let formData = new FormData();
    formData.append("model", input.current.files[0]);
    props.setLoading(true);
    axios
      .put("http://127.0.0.1:5000/api/init_model", formData, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Content-Type": "multipart/form-data",
        },
      })
      .then(() => {
        props.setLoading(false);
        props.setModelInitialised(true);
      })
      .catch((err) => console.log(err));
  };

  return (
    <div
      className={
        props.visible && !props.loading ? "init-model-page" : "invisible"
      }
    >
      <div className="button-container">
        <div className="button" onClick={init_model_on_seed}>
          <label className="button-txt"> New model </label>
        </div>
      </div>
      <form className="file-submission-form button-container">
        <label htmlFor="pkl-input" className="button" accept=".pkl">
          <h2 className="btn-title"> Load Model </h2>
        </label>
        <input
          ref={input}
          id="pkl-input"
          name="model-file"
          type="file"
          onChange={load_model_from_file}
        />
      </form>
    </div>
  );
}
