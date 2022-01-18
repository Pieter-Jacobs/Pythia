import CSVReader from "react-csv-reader";
import DatasetView from "./Components/DatasetView.js";
import ModelChoice from "./Components/ModelChoice.js";
import QueryView from "./Components/QueryView.js";
import DataDownloadView from "./Components/DataDownloadView";
import spinner from "./icons/Spinner.svg";
import { useState, useEffect } from "react";
import axios from 'axios';
import "./App.css";
import 'font-awesome/css/font-awesome.min.css';

export default function App(props) {
  const [title, setTitle] = useState("Pythia");
  const [modelInitialised, setModelInitialised] = useState(false);
  const [columnsSelected, setColumnsSelected] = useState(false);
  const [buttonVisible, setVisible] = useState(true);
  const [loading, setLoading] = useState(false);
  const [queried, setQueried] = useState(false);
  const [data, setData] = useState([{ Title: "" }]);

  // copy same regex used by parse
  const FLOAT = /^\s*-?(\d*\.?\d+|\d+\.?\d*)(e[-+]?\d+)?\s*$/i;
  const ISO_DATE = /(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))/;

  // rewrite parseDynamic to return undefined
  let parseDynamicReturningUndefined = (value, field) => {
    if (value === "true" || value === "TRUE") {
      return true;
    } else if (value === "false" || value === "FALSE") {
      return false;
    } else if (FLOAT.test(value)) {
      return parseFloat(value);
    } else if (ISO_DATE.test(value)) {
      return new Date(value);
    } else return value === "" ? null : value;
  };


  return (
    <div className="App">
      <header>
        <h1 className="title">{title}</h1>
        <div className="line-container">
          <hr className="line yellow"></hr>
          <hr className="line pink"></hr>
        </div>
      </header>
      <img className={loading ? "spinner" : "invisible"} src={spinner} />
      <label
        className={buttonVisible ? "button-container" : "invisible"}
        htmlFor="react-csv-reader-input"
      >
        <CSVReader
          cssClass="button"
          label="Upload CSV"
          inputStyle={{ color: "red" }}
          parserOptions={{
            header: true,
            transform: parseDynamicReturningUndefined,
          }}
          onFileLoaded={(data, fileInfo) => {
            setData(data);
            setVisible(false);
            if(Object.keys(data[0]).length <= 4) {
              setTitle("Please select the text-column");
            } else {
              setTitle("Please select the columns to be used");
            }
          }}
        />
      </label>
        <DatasetView
          setLoading={setLoading}
          setColumnsSelected={setColumnsSelected}
          setTitle={setTitle}
          visible={!buttonVisible && !columnsSelected && !loading}
          data={data}
        />
        <ModelChoice
          loading={loading}
          setLoading={setLoading}
          setModelInitialised={setModelInitialised}
          setTitle={setTitle}
          visible={columnsSelected && modelInitialised === false && !loading}
        />
      {modelInitialised === true && (
        <QueryView
          visible={!loading && !queried}
          setLoading={setLoading}
          setQueried={setQueried}
          setTitle={setTitle}
        />
      )}
      {queried && (<DataDownloadView
        setTitle={setTitle}
        setLoading={setLoading}
        loading={loading}
        visible={true}
      />
      )}
    </div>
  );
}
