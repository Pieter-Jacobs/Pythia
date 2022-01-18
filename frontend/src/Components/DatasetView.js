import React from "react";
import axios from "axios";
import DropdownButton from "react-bootstrap/DropdownButton";
import Dropdown from "react-bootstrap/Dropdown";
import { useState, useEffect } from "react";

export default function ColumnView(props) {
  const [columns, setColumns] = useState([]);
  const [textChosen, setTextChosen] = useState(false);
  const [labelChosen, setLabelChosen] = useState(false);
  const [selectedLabelCol, setSelectedLabelCol] = useState(null)
  const [selectedTextCol, setSelectedTextCol] = useState(null)

  useEffect(() => {
    if (columns.length === 2) {
      props.setLoading(true);
      axios
        .post(
          "http://127.0.0.1:5000/api/preprocess",
          {
            file: props.data,
            columns: columns,
          },
          {
            headers: {
              "Access-Control-Allow-Origin": "*",
            },
          }
        )
        .then(() => {
          props.setLoading(false);
          props.setColumnsSelected(true);
        })
        .catch((err) => console.log(err));
    }
  }, [columns]);

  let handleClick = (e) => {
    e.target.className = "column selected";
    setColumns([...columns, parseInt(e.target.id)]);
    props.setTitle("Please select the label-column");
  };

  let handleDropdownTextClick = (e) => {
    e.target.parentElement.previousElementSibling.innerHTML =
      e.target.innerHTML;
    const idx = parseInt(e.target.id)
    setSelectedTextCol(idx);
    if (textChosen) {
      setColumns([idx]);
    } else {
      setColumns([idx, ...columns]);
      setTextChosen(true);
    }
  };

  let handleDropdownLabelClick = (e) => {
    e.target.parentElement.previousElementSibling.innerHTML =
      e.target.innerHTML;
    const idx = parseInt(e.target.id)
    setSelectedLabelCol(idx)
    if (labelChosen) {
      setColumns([idx]);
    } else {
      setColumns([...columns, idx]);
      setLabelChosen(true);
    }
  };
  return (
    <div className={props.visible ? "dataset-view" : "invisible"}>
      <div
        className={
          Object.keys(props.data[0]).length <= 4
            ? "column-container"
            : "invisible"
        }
      >
        {Object.keys(props.data[0]).map((key, i) => (
          <div onClick={handleClick} id={i} className="column">
            <h2>{key}</h2>
          </div>
        ))}
      </div>
      <div
        className={
          Object.keys(props.data[0]).length > 4
            ? "dropdown-container"
            : "invisible"
        }
      >
        <Dropdown id="column-dropdown">
          <Dropdown.Toggle variant="success" id="dropdown-basic-button">
            Select the text column <i className="fa fa-chevron-down"></i>
          </Dropdown.Toggle>

          <Dropdown.Menu>
            {Object.keys(props.data[0]).map((key, i) => (
              <Dropdown.Item
                id={i}
                className={i == selectedTextCol ? "column selected" : "column"}
                onClick={handleDropdownTextClick}
              >
                {key}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
        <Dropdown id="label-dropdown">
          <Dropdown.Toggle variant="success" id="dropdown-basic-button">
            Select the label column <i class="fa fa-chevron-down"></i>
          </Dropdown.Toggle>
          <Dropdown.Menu>
            {Object.keys(props.data[0]).map((key, i) => (
              <Dropdown.Item
                id={i}
                className={i == selectedLabelCol ? "column selected" : "column"}
                onClick={handleDropdownLabelClick}
              >
                {key}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      </div>
    </div>
  );
}
