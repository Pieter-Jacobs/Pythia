import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function DataDownloadView(props) {
  let input = useRef();
  const [formShown, setFormShown] = useState(false);

  useEffect(() => {
    if (props.visible) {
      props.setTitle("Dataset labeled!");
    }
  }, []);


  const handleModelSave = async (e) => {
    e.preventDefault();
    setFormShown(null);
    const filename = input.current.value;
    props.setLoading(true);
    await axios
      .put("http://127.0.0.1:5000/api/save_model_to_file", {
        filename: filename,
      })
      .then(() => {
        props.setLoading(false);
        setFormShown(false);
      });
  };

  return (
    <div className={props.visible ? "data-download-page" : "invisible"}>
      <div className={!formShown && !props.loading ? "button-container" : "invisible"}>
        <a href="http://127.0.0.1:5000/api/get_labeled_csv">
          <div className="button">
            <label className="button-txt"> Download Data </label>
          </div>
        </a>
      </div>
      <div className={!formShown && !props.loading ? "button-container" : "invisible"}>
        <div className="button" onClick={() => setFormShown(true)}>
          <label className="save-model-txt"> Save model </label>
        </div>
      </div>
      <form
        className={formShown && !props.loading ? "save-model-form" : "invisible"}
        onSubmit={handleModelSave}
      >
        <input
          className="filename-input"
          ref={input}
          type="text"
          name="filename"
          placeholder="Filename..."
        />
        <input type="submit" className="model-submit" />
      </form>
    </div>
  );
}
