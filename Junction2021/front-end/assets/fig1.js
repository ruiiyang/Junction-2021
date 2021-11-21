
var chartDom = document.getElementById('fig1');
var myChart = echarts.init(chartDom);
var option;

option = {
    series: [{
        type: 'liquidFill',
        data: [0.6]
    }]
};

myChart.setOption(option);
