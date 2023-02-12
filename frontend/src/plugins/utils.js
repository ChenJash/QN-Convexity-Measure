import * as d3 from "d3";

function begin_loading() {
    // $(".loading").show();
    // $(".loading-svg").show();
    d3.select(".loading")
        .style("display", "block");
    d3.select(".loading-svg")
        .style("display", "block");
}

function end_loading(delay) {
    delay = delay || 1;
    // console.log("delay", delay);
    d3.select(".loading")
        .transition()
        .duration(1)
        .delay(delay)
        .style("display", "none");
    d3.select(".loading-svg")
        .transition()
        .duration(1)
        .delay(delay)
        .style("display", "none");
}

export {
    begin_loading,
    end_loading
}