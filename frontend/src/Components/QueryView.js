import React, { useEffect, useState } from "react";
import LineChart from "./LineChart.js";
import axios from "axios";

const getLabelMapping = async () => {
  const label_mapping_obj = await axios.get(
    "http://127.0.0.1:5000/api/get_label_mapping"
  );
  return label_mapping_obj.data;
};

const getQueryData = async () => {
  let queryData = await axios.get("http://127.0.0.1:5000/api/take_al_step");
  let text_arr = Object.values(queryData.data.texts).map((value) => value);
  let preds = Object.values(queryData.data.preds).map((value) =>
    Object.values(value).map((val) => val)
  );
  return [text_arr, queryData.data.uncertainty, preds];
};

export default function QueryView(props) {
  const [uncertainty, setUncertainty] = useState(5);
  const [showingGraph, setShowingGraph] = useState(false);
  const [texts, setTexts] = useState([""]);
  const [preds, setPreds] = useState([]);
  const [labels, setLabels] = useState(null);
  const [label_mapping, setLabelMapping] = useState([]);
  const K = 10;

  useEffect(() => {
    async function fetchLabelMap() {
      setLabelMapping(await getLabelMapping());
    }
    fetchLabelMap();
    props.setTitle("Please label this text");
  }, []);

  useEffect(() => {
    if (uncertainty < 0.1) {
      classifyUnlabeledData();
      props.setQueried(true);
    }
  }, [uncertainty]);

  useEffect(() => {
    async function fetchTexts() {
      if (labels === null || labels.length === K) {
        if (!(labels === null) && labels.length === K) {
          await axios.post("http://127.0.0.1:5000/api/label_examples", {
            labels: labels,
          });
        }
        props.setLoading(true);
        let queryData = await getQueryData();
        setTexts(queryData[0]);
        setUncertainty(queryData[1]);
        setPreds(queryData[2]);
        props.setLoading(false);
        setLabels([]);
      }
    }
    fetchTexts();
  }, [labels]);

  let handleLabelSelection = (e) => {
    const label = e.target.children[0].innerText;
    setLabels([...labels, label]);
    let newTexts = texts.slice(1);
    let newPreds = preds.slice(1);
    setTexts(newTexts);
    setPreds(newPreds);
  };

  const classifyUnlabeledData = async () => {
    props.setLoading(true);
    await axios.put("http://127.0.0.1:5000/api/classify_unlabeled_data");
    props.setLoading(false);
    props.setQueried(true);
  };

  return (
    <div className={props.visible ? "query-container" : "invisible"}>
      <h2 className="queried-text">{texts[0]}</h2>
      <div className="column-container label-choice-container">
        <h1>{label_mapping[0]}</h1>
        {Object.keys(label_mapping).map((label, i) => (
          <div onClick={handleLabelSelection} className="column">
            <h2>{label}</h2>
            <h3 className="softmax-probability">
              {preds.length != 0 ? preds[0][i] + "%" : null}
            </h3>
          </div>
        ))}
      </div>
      <div className="button-container" id="classify-btn-container">
        <div className="button" onClick={classifyUnlabeledData}>
          <label className="classify-txt"> Classify </label>
        </div>
      </div>
      <div
        className="chart-button"
        onClick={() => setShowingGraph(!showingGraph)}
      >
        <i
          className="fa fa-3x fa-bar-chart"
          onClick={() => setShowingGraph(true)}
        ></i>
      </div>
      {uncertainty != 5 && (
        <LineChart
          visible={showingGraph}
          setShowingGraph={setShowingGraph}
          uncertainty={uncertainty}
          K={K}
        />
      )}
    </div>
  );
}
