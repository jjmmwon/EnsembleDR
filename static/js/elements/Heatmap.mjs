export { Heatmap };

class Heatmap {
    constructor(div, width = 300, height = 300) {
        this.div = div;
        this.width = width;
        this.height = height;
        this.margin = {
            top: 20,
            right: 20,
            bottom: 20,
            left: 20,
        };
        this.k = [5, 7, 10, 15, 20];
        this.minSupport = [6, 7, 8, 9, 10];
        this.handlers = {};
    }

    initialize() {
        this.div = d3.select(this.div).append('div');
        this.svg = this.div.append('svg');
        this.container = this.svg.append('g');
        this.xAxis = this.svg.append('g');
        this.yAxis = this.svg.append('g');

        this.svg.attr('width', this.width).attr('height', this.height);

        this.container.attr(
            'transform',
            `translate(${this.margin.left}, ${this.margin.top})`
        );

        this.xScale = d3
            .scaleBand()
            .domain(this.minSupport)
            .range([0, this.width - this.margin.left - this.margin.right])
            .padding(0.01);

        this.yScale = d3
            .scaleBand()
            .domain(this.k)
            .range([0, this.height - this.margin.top - this.margin.bottom])
            .padding(0.01);

        this.colorScale = d3
            .scaleLinear()
            .range(['white', '#69b3a2'])
            .domain([1, 200]);

        this.xAxis
            .attr(
                'transform',
                `translate(${this.margin.left}, ${this.margin.top})`
            )
            .call(d3.axisTop(this.xScale));

        this.yAxis
            .attr(
                'transform',
                `translate(${this.margin.left}, ${this.margin.top})`
            )
            .call(d3.axisLeft(this.yScale));

        this.kBand = this.k.map((d) => this.yScale(d));
        this.msBand = this.minSupport.map((d) => this.xScale(d));

        return this;
    }

    update(fsm) {
        this.container
            .selectAll('rect')
            .data(fsm)
            .join('rect')
            .attr('x', (d) => this.xScale(d['min_support']))
            .attr('y', (d) => this.yScale(d['k']))
            .attr('width', this.xScale.bandwidth())
            .attr('height', this.yScale.bandwidth())
            .style('fill', (d) => this.colorScale(d['FS'].length))
            .on('click', (event) => this.clickCell(event));

        return this;
    }

    on(eventType, handler) {
        this.handlers[eventType] = handler;
    }

    clickCell(event) {
        let [x, y] = d3.pointer(event);
        let xVal = this.minSupport[4],
            yVal = this.k[4];

        this.msBand.forEach((d, i) => {
            if (xVal == this.minSupport[4])
                xVal = x < d ? this.minSupport[i - 1] : xVal;
        });

        this.kBand.forEach((d, i) => {
            if (yVal == this.k[4]) yVal = y < d ? this.k[i - 1] : yVal;
        });

        if (this.handlers?.click) {
            this.handlers.click(yVal, xVal);
        }
    }
}
