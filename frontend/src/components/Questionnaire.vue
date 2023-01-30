<template>
  <div class="question-naire">
    <svg id="main-svg">
    </svg>
  </div>
</template>

<script>
import axios from 'axios';
import * as d3 from 'd3';
window.d3 = d3;
export default {
    name: 'QuestionNaire',
    computed: {
        svg: function() {
            return d3.select('#main-svg');
        },
    },
    data() {
        return {
            user_id: -1,
            nxt_index: -1,
            data: {},
            history: [],
            change_result: false,
            enable_next: false,
            options: [
                {
                    id: 'A',
                    x: 560,
                    y: 136
                }, {
                    id: 'B',
                    x: 1004,
                    y: 136
                }, {
                    id: 'C',
                    x: 560,
                    y: 499
                }, {
                    id: 'D',
                    x: 1004,
                    y: 499
                }
            ],
            selected: [],
            cur_select: 0,
            select_colors: ['#DE0707', '#0F40F5', '#A16222', '#81B337'], 
            select_state: [false, false, false, false],
            buttons: [{
                id: 0,
                text: 'Clear',
                y: 865
            }, {
                id: 1,
                text: 'Previous',
                y: 919
            }, {
                id: 2,
                text: 'Next',
                y: 973
            }],
            raw_grid: {},
            grids: [],
            items: [],
            links: [],
            drag_info: {},
            grid_width: 300,
            rank_width: 1146,
            create_duration: 500,
            update_duration: 500,
            remove_duration: 500,
            trans: {
                "A": 1, "B": 2, "C": 3, "D": 4
            }
        };
    },
    watch: {
        data: function(){
            // console.log('data change', this.data);
            this.layout();
            this.render();
            this.loadHistory();
            this.enableButton();
        },
        selected: function() {
            this.itemLayout();
            this.itemRender();
            if(this.selected.length === 0) this.enable_next = false;
            else this.enable_next = true;
            this.enableButton();
            this.change_result = true;
        },
        nxt_index: function() {
            // clear first
            this.cur_select = 0;
            this.selected = [];
            this.select_state = [false, false, false, false];
            this.svg.selectAll('.grid-group')
                .select('.boundary')
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0);
            this.getData();
        }
    },
    methods: {
        // authentication
        login: async function(){
            const that = this;
            await axios.post('/api/login', {
            }).then(function(response) {
                console.log('Login user id:', response.data.user_id);
                that.user_id = response.data.user_id;
            });
        },
        // data fetch functions
        getHackData: function() {
            const that = this;
            axios.post('/api/hack-data', {
            }).then(function(response) {
                console.log('Get hack data:', response);
                that.data = response.data;
            });
        },
        getData: function() {
            const that = this;
            axios.post('/api/get-data', {
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    console.log('Get data error:', response.data.detail);
                }
                else{
                    console.log('Get data:', response.data);
                    that.data = response.data.data;
                    that.history = response.data.history;
                }
            });
        },
        submit: async function() {
            await axios.post('/api/submit', {
                result: this.selected
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    console.log('Submit error:', response.data.detail);
                }
                else{
                    console.log('Submit success.');
                }
            });
        },
        changeQuestion: async function(nxt) {
            const that = this;
            await axios.post('/api/change-question', {
                index: nxt
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    console.log('Change error:', response.data.detail);
                }
                else{
                    console.log('Change success.');
                    that.nxt_index = nxt;
                }
            });
        },
        loadHistory: function() {
            const history = this.history;
            this.change_result = false;
            if(history.length === 0) return;
            history.forEach((item) => {
                item.color_id = this.select_colors.indexOf(item.color);
                this.select_state[item.color_id] = true;
                this.svg.selectAll('.grid-group')
                    .filter(e => e.id === this.trans[item.option])
                    .select('.boundary')
                    .attr('stroke', item.color)
                    .attr('opacity', 1);
                this.grids[this.trans[item.option] - 1].selected = true
            })
            this.cur_select = this.select_state.indexOf(false);
            this.selected = history;
        },
        // layout functions
        layout: function() {
            if(this.data.grids === undefined) return;
            const size = this.data.grids[0].length;
            const width_size = Math.floor(Math.sqrt(size));
            console.assert(width_size * width_size === size, 'Error grid size.');
            const cell_width = this.grid_width / width_size;
            const grids = [];
            this.data.grids.forEach((elements, index) => {
                const grid = {};
                grid.id = index;
                grid.width_size = width_size;
                grid.cell_width = cell_width;
                if(index > 0) {
                    grid.option = this.options[index-1];
                }
                const cells = [];
                let i = 0; let j = 0;
                elements.forEach((element, eindex) => {
                    const cell = {};
                    cell.id = eindex;
                    cell.pos = [j, i].concat();
                    cell.element = element;
                    cell.label = this.data.labels[element];
                    cell.color = this.data.colors[cell.label];
                    cell.width = cell_width;
                    i = (i + 1) % width_size;
                    if(i == 0) j = j + 1;
                    cells.push(cell);
                })
                grid.cells = cells;
                grid.name = `${this.data.index}-${index}`
                grids.push(grid);
            })
            this.raw_grid = grids[0];
            this.raw_grid.index = this.data.index;
            this.grids = grids.slice(1);
        },
        itemLayout: function() {
            let divide_size = this.selected.length + 1;
            if(this.selected.length > 0) {
                divide_size += (this.selected.length - 1);
            }
            const item_gap = this.rank_width / divide_size;
            this.items = this.selected.map((op, index) => {
                const item = {};
                item.name = `${op.option}-${op.color}`;
                item.option = op.option;
                item.color = op.color;
                item.sequence = index;
                item.x = item_gap * (2 * index + 1) - 67;
                item.y = 30; 
                item.equal = op.equal.concat();
                item.raw = op;
                return item;
            })
            this.links = [];
            this.items.forEach((op, index, array) => {
                if(index == 0) return;
                const link = {};
                link.start = array[index - 1];
                link.end = array[index];
                link.name = `${link.start.name}--${link.end.name}`;
                link.x = (link.start.x + link.end.x) / 2 + 67;
                link.y = 54;
                link.value = '>';
                if(link.start.equal[1] && link.end.equal[0]) link.value = '=';
                this.links.push(link);
            })
        },
        // render functions
        initRender: function() {
            this.svg.attr('width', 1440)
                .attr('height', 1024);
            // background
            this.svg.append('text')
                .text('Judge Convexity in Grid Layout')
                .attr('x', 57)
                .attr('y', 51)
                .attr('font-size', 28);
            this.svg.append('rect')
                .attr('x', 57)
                .attr('y', 86)
                .attr('width', 1323)
                .attr('height', 758)
                .attr('rx', 20)
                .attr('ry', 20)
                .attr('fill', 'rgba(239,239,239,0.1')
                .attr('stroke', 'rgb(187,187,187)')
                .attr('stroke-width', 1);
            this.svg.append('text')
                .text('Select options with the best convexity')
                .attr('x', 81)
                .attr('y', 120)
                .attr('font-size', 20);
            this.svg.append('text')
                .text('and sort them:')
                .attr('x', 81)
                .attr('y', 147)
                .attr('font-size', 20);
            this.svg.append('text')
                .text('Raw grid:')
                .attr('x', 81)
                .attr('y', 292)
                .attr('font-size', 20);
            this.svg.append('rect')
                .attr('x', 57)
                .attr('y', 884)
                .attr('width', 1146)
                .attr('height', 108)
                .attr('rx', 20)
                .attr('ry', 20)
                .attr('fill', 'rgba(255,191,107,0.1')
                .attr('stroke', 'rgb(187,187,187)')
                .attr('stroke-width', 1);
            this.svg.append('g')
                .attr('class', 'rank-group')
                .attr('width', 1146)
                .attr('height', 108)
                .attr('transform', 'translate(57, 884)');
            // buttons
            const buttons = this.svg.selectAll('.qn-buttons')
                .data(this.buttons)
                .enter()
            const button = buttons.append('g')
                .attr('class', 'qn-buttons')
                .attr('transform', d => `translate(${1238},${d.y})`)
                .on('mouseover', this.highlightButton)
                .on('mouseout', this.dehighlightButton)
                .on('click', this.clickButton)
                .style('cursor', 'pointer');
            button.append('rect')
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', 142)
                .attr('height', 39)
                .attr('fill', 'rgb(255,255,255)')
                .attr('stroke', 'rgb(187,187,187)')
                .attr('stroke-width', 1);
            button.append('text')
                .text(d => d.text)
                .attr('x', 71)
                .attr('y', 26)
                .attr('font-size', 18)
                .attr('text-anchor', 'middle');
            const button3 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 2);
            button3.select('rect')
                .attr('fill', 'rgba(239,239,239,0.67)');
            button3.select('text')
                .attr('fill', 'rgba(108,108,108,0.72)');
        },
        gridRender: function(group) {
            group.enter()
                .append('rect')
                .attr('class', 'grid-cell')
                .attr('x', d => d.pos[0] * d.width)
                .attr('y', d => d.pos[1] * d.width)
                .attr('width', d => d.width)
                .attr('height', d => d.width)
                .attr('fill', d => `rgb(${d.color[0] * 255},${d.color[1] * 255},${d.color[2] * 255})`)
                .attr('stroke', 'black')
                .attr('stroke-width', 1)
                .attr('opacity', 0)
                .transition()
                .duration(this.create_duration / 3)
                .delay(this.remove_duration / 3)
                .attr('opacity', 1);
            group.transition()
                .duration(this.update_duration)
                .attr('x', d => d.pos[0] * d.width)
                .attr('y', d => d.pos[1] * d.width)
                .attr('width', d => d.width)
                .attr('height', d => d.width)
                .attr('fill', d => `rgb(${d.color[0] * 255},${d.color[1] * 255},${d.color[2] * 255})`)
            group.exit()
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove()
        },
        render: function() {
            // render raw grid
            const raw_group = this.svg.selectAll('.raw-grid')
                .data([this.raw_grid], d => d.index);
            const raw_create = raw_group.enter()
                .append('g')
                .attr('class', 'raw-grid')
                .attr('transform', 'translate(121, 317)');
                // .style('cursor', 'pointer');
            raw_group.exit()
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove()
            let merge_group = raw_group.merge(raw_create);
            let grid_group = merge_group.selectAll('rect')
                .data(d => d.cells, c => c.id);
            this.gridRender(grid_group);

            // render grids
            const grids_group = this.svg.selectAll('.grid-group')
                .data(this.grids, d => d.name);
            const grids_create = grids_group.enter()
                .append('g')
                .attr('class', 'grid-group')
                .attr('transform', d => `translate(${d.option.x}, ${d.option.y})`)
                .style('cursor', 'pointer')
                .on('mouseover', this.highlightOption)
                .on('mouseout', this.dehighlightOption)
                .on('click', this.clickOption);
            grids_create.append('text')
                .text(d => `${d.option.id}.`)
                .attr('x', -30)
                .attr('y', 15)
                .attr('font-size', 20);
            grids_create.append('rect')
                .attr('class', 'boundary')
                .attr('x', -42)
                .attr('y', -15)
                .attr('width', 361)
                .attr('height', 330)
                .attr('rx', 11)
                .attr('ry', 11)
                .attr('fill-opacity', 0)
                .attr('stroke', 'gray')
                .attr('stroke-width', 2)
                .attr('opacity', 0);
            grids_group.exit()
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove();
            merge_group = grids_group.merge(grids_create);
            grid_group = merge_group.selectAll('.grid-cell')
                .data(d => d.cells, c => c.id);
            this.gridRender(grid_group);
        },
        itemRender: function() {
            // render items
            const item_group = this.svg.select('.rank-group')
                .selectAll('.item-group')
                .data(this.items, d => d.name);
            const drag_solver = d3.drag()
                .on('start', (ev, d) => {
                    this.svg.selectAll('.item-group')
                        .filter(e => e.name === d.name).raise();
                    this.drag_info.rx = ev.x;
                    this.drag_info.ry = ev.y;
                })
                .on('drag', (ev, d) => {
                    this.svg.selectAll('.item-group')
                        .filter(e => e.name === d.name)
                        .attr('transform', `translate(${d.x + ev.x - this.drag_info.rx}, ${d.y + ev.y - this.drag_info.ry})`);
                })
                .on('end', (ev, d) => {
                    let direct = 'left';
                    if(ev.x > this.drag_info.rx) direct = 'right';
                    d.x = d.x + ev.x - this.drag_info.rx;
                    d.y = d.y + ev.y - this.drag_info.ry;
                    if(direct == 'left') {
                        let i = 0;
                        for(;i < this.items.length;i++){
                            if(this.items[i].x + 67 > d.x){
                                i--; break;
                            }
                        }
                        let j = this.selected.findIndex(e => e.option === d.option);
                        const target = [].concat(this.selected.slice(0, i+1), [this.selected[j]],
                            this.selected.slice(i+1, j), this.selected.slice(j+1));
                        this.selected[j].equal = [false, false];
                        this.selected = target;
                    }
                    else{
                        let i = this.items.length - 1;
                        for(;i > -1;i--){
                            if(this.items[i].x < d.x + 67){
                                i++; break;
                            }
                        }
                        let j = this.selected.findIndex(e => e.option === d.option);
                        const target = [].concat(this.selected.slice(0, j), this.selected.slice(j+1, i),
                            [this.selected[j]], this.selected.slice(i));
                        this.selected[j].equal = [false, false];
                        this.selected = target;
                    }
                    this.drag_info = {};
                });
            const item_create = item_group.enter().append('g')
                .attr('class', 'item-group')
                .attr('transform', d => `translate(${d.x}, ${d.y})`)
                .style('cursor', 'pointer')
                .call(drag_solver);
            item_create.append('rect')
                .attr('x', 0)
                .attr('y', 0)
                .attr('stroke', d => d.color)
                .attr('rx', 20)
                .attr('ry', 20)
                .attr('stroke-width', 4)
                .attr('width', 134)
                .attr('height', 46)
                .attr('fill', 'white');
            item_create.append('text')
                .text(d => d.option)
                .attr('x', 67)
                .attr('y', 30)
                .attr('fill', d => d.color)
                .attr('font-size', 25)
                .attr('text-anchor', 'middle')
                .attr('font-weight', 'bold');
            item_create.attr('opacity', 0)
                .transition()
                .duration(this.create_duration)
                .attr('opacity', 1);
            item_group.transition()
                .duration(this.update_duration)
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            item_group.exit()
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove();
            
            // render links
            const link_group = this.svg.select('.rank-group')
                .selectAll('.link-group')
                .data(this.links, d => d.name);
            const link_create = link_group.enter().append('g')
                .attr('class', 'link-group')
                .attr('transform', d => `translate(${d.x}, ${d.y})`)
                .style('cursor', 'pointer')
                .on('click', this.clickLink);
            link_create.append('circle')
                .attr('cx', 0)
                .attr('cy', 0)
                .attr('r', 32)
                .attr('stroke', 'rgba(108,108,108, 0.57)')
                .attr('stroke-width', 1)
                .attr('fill', 'rgba(254,250,131,0.73)');
            link_create.append('text')
                .text(d => d.value)
                .attr('x', 0)
                .attr('y', 14)
                .attr('fill', d => d.color)
                .attr('font-size', 36)
                .attr('text-anchor', 'middle')
                .attr('font-weight', 'bold')
                .attr('fill', '#9A9A9A');
            link_create.attr('opacity', 0)
                .transition()
                .duration(this.create_duration)
                .attr('opacity', 1);
            link_group.transition()
                .duration(this.update_duration)
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            link_group.select('text')
                .transition()
                .duration(this.update_duration)
                .text(d => d.value);
            link_group.exit()
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove();
        },
        enableButton: function(){
            const button2 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 1);
            if(this.data.index > 0) {
                button2.select('rect').attr('fill', 'rgb(255,255,255)');
                button2.select('text').attr('fill', 'black');
            }
            else {
                button2.select('rect').attr('fill', 'rgba(239,239,239,0.67)');
                button2.select('text').attr('fill', 'rgba(108,108,108,0.72)');
            }
            const button3 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 2);
            if(this.enable_next) {
                button3.select('rect').attr('fill', 'rgb(255,255,255)');
                button3.select('text').attr('fill', 'black');
            }
            else {
                button3.select('rect').attr('fill', 'rgba(239,239,239,0.67)');
                button3.select('text').attr('fill', 'rgba(108,108,108,0.72)');
            }
        },
        // interaction functions
        highlightButton: function(ev, d) {
            if(this.data.index === 0 && d.id == 1) return;
            if(!this.enable_next && d.id == 2) return;
            const button = this.svg.selectAll('.qn-buttons').filter(e => e.id === d.id);
            button.select('rect')
                .attr('stroke', 'blue')
                .attr('stroke-width', 2);
        },
        dehighlightButton: function(ev, d) {
            const button = this.svg.selectAll('.qn-buttons').filter(e => e.id === d.id);
            button.select('rect')
                .attr('stroke', 'rgb(187,187,187)')
                .attr('stroke-width', 1);
        },
        clickButton: async function(ev, d) {
            if(d.id == 0){
                // click 'clear'
                this.grids.forEach((grid) => {
                    grid.selected = false;
                });
                this.cur_select = 0;
                this.selected = [];
                this.select_state = [false, false, false, false];
                this.svg.selectAll('.grid-group')
                    .select('.boundary')
                    .attr('opacity', 0);
                return;
            }
            if(this.data.index === 0 && d.id == 1) return;
            if(!this.enable_next && d.id == 2) return;
            if(this.enable_next && this.change_result) {
                // submit current result
                await this.submit();
            }
            let nxt = this.data.index;
            if(d.id == 1) nxt -= 1;
            else nxt += 1;
            await this.changeQuestion(nxt);
        },
        highlightOption: function(ev, d) {
            if(d.selected == true) return;
            this.svg.selectAll('.grid-group')
                .filter(e => e.id === d.id)
                .select('.boundary')
                .attr('stroke', this.select_colors[this.cur_select])
                .attr('opacity', 1);
        },
        dehighlightOption: function(ev, d) {
            if(d.selected == true) return;
            this.svg.selectAll('.grid-group')
                .filter(e => e.id === d.id)
                .select('.boundary')
                .attr('opacity', 0);
        },
        clickOption: function(ev, d) {
            if(d.selected == true){
                const idx = this.selected.findIndex(e => e.option === d.option.id);
                this.select_state[this.selected[idx].color_id] = false;
                this.selected.splice(idx, 1);
                d.selected = false;
                this.cur_select = this.select_state.indexOf(false);
                this.dehighlightOption(ev, d);
                return;
            }
            this.selected.push(
                {
                    option: d.option.id,
                    color: this.select_colors[this.cur_select],
                    color_id: this.cur_select,
                    equal: [false, false]
                }
            );
            this.select_state[this.cur_select] = true;
            this.cur_select = this.select_state.indexOf(false);
            d.selected = true;
        },
        clickLink: function(ev, d) {
            if(d.value === '>'){
                d.start.raw.equal[1] = true;
                d.end.raw.equal[0] = true;
            }
            else{
                d.start.raw.equal[1] = false;
                d.end.raw.equal[0] = false;
            }
            this.itemLayout();
            this.itemRender();
        }
    },
    async mounted() {
        await this.login();
        // this.getHackData();
        this.getData();
        this.initRender();
    },
}
</script>

<style>
.question-naire {
    width: 100%;
    height: 100%;
    justify-content: center;
    align-items: center;
    position: relative;
}
</style>