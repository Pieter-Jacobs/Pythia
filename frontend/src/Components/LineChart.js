import { React, useState, useEffect } from "react";
import {
  FlexibleXYPlot,
  XAxis,
  YAxis,
  ChartLabel,
  LineSeries,
  LineSeriesCanvas,
} from "react-vis";
import "react-vis/dist/style.css";

let n_labeled = 0;

export default function LineChart(props) {
  const [data, setData] = useState([]);
  useEffect(() => {
    setData([...data, { x: n_labeled, y: props.uncertainty}]);
    n_labeled += props.K;
  }, [props.uncertainty]);
  return (
    <div className={props.visible ? "uncertainty-plot" : "invisible"}>
      <FlexibleXYPlot
        yDomain={[0,1]}
        height={300}
        width={300}
      >
        <XAxis />
        <YAxis />
        {console.log(data)}
        <LineSeries data={data} />
        <ChartLabel
          text="Amount of labeled examples"
          className="alt-x-label"
          includeMargin={false}
          xPercent={0.025}
          yPercent={1.01}
        />

        <ChartLabel
          text="Average uncertainty"
          className="alt-y-label"
          includeMargin={false}
          xPercent={-0.1}
          yPercent={0.4}
          style={{
            transform: "rotate(-90)",
            textAnchor: "end",
            color: "white",
            fill: "white",
          }}
        />
      </FlexibleXYPlot>
      <i
        className="fa fa-4x fa-times"
        onClick={() => props.setShowingGraph(false)}
      ></i>
    </div>
  );
}
