<template>
  <div class="question-naire">
    <el-dialog title="Tutorial" :visible.sync="tutorial" width="1300px" class="form" :before-close="closeTutorial">
        <video width="1250" height="630" controls>
            <source src="../assets/mp4/grid_tutorial_v2.mp4" />
        </video>
    </el-dialog>
    <el-dialog title="Consent Form" :visible.sync="consent_form" width="1300px" :show-close="false" 
            :close-on-press-escape="false" :close-on-click-modal="false" class="form" id="consent">
        
        <el-form label-position="left" label-width="1000px" :model="consent_result">
        <el-form-item class="item">
            <template slot="label">1.	I confirm that I have read and have understood the <span id="sheet-link" @click="info_sheet=true">information sheet</span> dated February 9, 2023 for the above study. I have had the opportunity to consider the information, ask questions and have had these answered satisfactorily.</template>
            <el-checkbox v-model="consent_result.agree1">Agree</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="2.	I understand that my participation is voluntary and that I am free to withdraw at any time without giving any reason, without my rights being affected.">
            <el-checkbox v-model="consent_result.agree2">Agree</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="3.	I understand that I can at any time ask for access to the information I provide and I can also request the destruction of that information if I wish.">
            <el-checkbox v-model="consent_result.agree3">Agree</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="4.	I agree to take part in the above study.">
            <el-checkbox v-model="consent_result.agree4">Agree</el-checkbox>
        </el-form-item>
        <el-button type="primary" @click="startQuestions">Start Answer!</el-button>
        </el-form>
    </el-dialog>
    <el-dialog title="Participant Information Sheet" :visible.sync="info_sheet" width="1300px" class="form" id="sheet">
        <p>You are being invited to participate in a research study. Before you decide whether to participate, it is important for you to understand why the research is being done and what it will involve. Please take time to read the following information carefully and feel free to ask us if you would like more information or if there is anything that you do not understand. Please also feel free to discuss this with your friends, relatives, and anyone else you wish. We would like to stress that you do not have to accept this invitation and should only agree to take part if you want to.</p>
        <p>The purpose of the study is to develop a grid layout method for better preserving cluster structures. According to Gestalt principles, people perceive convex shapes ahead of concave shapes. It is then desired to generate the layout result that makes each cluster more convex. This process requires a convexity measure. However, there is no yet generally accepted convexity measure, and we want to know which measure is more consistent with human perception. To do this, we need to have participants, like yourself, to see a set of grid layout results and then sort the results based on the convexity.</p>
        <p>While you perform the tasks, your interaction with the system will be in a safe environment and supervised by the professors or research students doing the project. The researchers will be always on the side to only observe and answer any questions and concerns you may have and to make sure all things are running as intended and that you are always comfortable and feeling safe at all times. </p>
        <p>The system will record automatically your sort results for later analyses. In addition, you may be asked to complete some simple questionnaires and answer some questions about your general experience and feelings about comparing the convexity of different grid layouts. The questions will not ask any personal information about you and if you feel uncomfortable with any question, it is quite alright if you choose not to answer. The user study will last about 1 hours.</p>
        <p>The data collected will help us understand how to design better grid layout algorithm that preserve the convexity of cluster shapes and will allow us to write reports and publish them as academic papers. If any reports and papers are published, they will not contain any information that can be used to identify any of the participants involved in our experiment.</p>
        <p>There will be other participants who will likely be THU and XJTLU students and their acquaintances. One of the benefits you and other participants will gain is to experience state-of-the-art technologies, like visualization, grid layout, and convexity measures.</p>
        <p>We want to make it clear to all our participants that they are not the ones being tested, but that we are only assessing the perceptions on convexity. Your participation is entirely voluntary, and you can stop at any time. </p>
        <p>If you are unhappy or if there is a problem, please feel free to let us know by contacting Dr. Lingyun Yu and we will try to help. If you remain unhappy or have a complaint with which you feel you cannot come to us, then you should contact the Chair of the Research Ethics Sub-Committee on ethics@xjtlu.edu.cn with enough details to help identify the project.</p>
    </el-dialog>
    <svg id="main-svg">
    </svg>
    <el-dialog title="Question Answer" :visible.sync="answer_dialog" width="1300px" @open="openDialog" @closed="closeDialog" class="form">
        <svg id="answer-svg" width="100%" height="570px">
            <g class="answer-nodes"></g>
            <g class="answer-links"></g>
        </svg>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import * as d3 from 'd3';
import * as Utils from "../plugins/utils";
window.d3 = d3;
export default {
    name: 'QuestionNaire',
    computed: {
        svg: function() {
            return d3.select('#main-svg');
        },
        d_svg: function() {
            return d3.select('#answer-svg')
        }
    },
    data() {
        return {
            // answer states
            is_first: false,
            is_normal: false,
            finish_all: false,
            repeat_view: false,
            // consent form
            consent_form: false,
            consent_result: {
                agree1: false,
                agree2: false,
                agree3: false,
                agree4: false
            },
            info_sheet: false,
            // tutorial
            tutorial: false,
            // questionnarie
            user_id: -1,
            cur_index: -1,
            nxt_index: -1,
            data: {},
            history: [],
            cur_pos: 0,
            total_length: [],
            change_result: -1,
            enable_next: false,
            options: [
                {
                    id: 'A',
                    x: 330,
                    y: 165
                }, {
                    id: 'B',
                    x: 850,
                    y: 165
                }, {
                    id: 'C',
                    x: 330,
                    y: 513
                }, {
                    id: 'D',
                    x: 850,
                    y: 513
                }
            ],
            selected: [],
            cur_select: 0,
            select_colors: ['#DE0707', '#0F40F5', '#A16222', '#81B337'], 
            select_state: [false, false, false, false],
            buttons: [{
                id: 0,
                text: 'Clear',
                y: 973
            }, {
                id: 1,
                text: 'Previous',
                y: 919
            }, {
                id: 2,
                text: 'Next',
                y: 865
            }],
            // raw_grid: {},
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
                'A': 0 ,'B': 1, 'C': 2, 'D': 3
            },
            trans2: ['A', 'B', 'C', 'D'],
            // dialogs
            answer_dialog: false,
            dialog_width: 1300,
            dialog_height: 570,
            dialog_nodes: [],
            dialog_links: [],
            dialog_texts: [],
            d_grid_width: 200,
            answer_data: [],
            tp_colors: [[29,178,231], [228,86,86], [79,217,92], [226,190,100]],
            // break time
            in_break: false,
            break_text: [[
                "Now you have six practice questions. There will be no time measurements.",
                "Once you have answered the questions, the correct answers and explanations will be displayed.",
                "To begin the <tspan fill='red'>practice session</tspan>, press the '<tspan fill='red'>Start</tspan>' button."
            ],[
                "Next, you will enter the <tspan fill='red'>formal user study</tspan>. In total, there are 36 questions",
                "that are divided into 4 groups. After each group, you may take a brief break.  ",
                "However, please ensure you <tspan fill='red'>complete all questions within the group without interruption</tspan>.",
                "In the formal user study, the questions will be more difficult than the simulation test.",
                "Each question may not have a standard answer, and each option has relatively good convexity.",
                "Rank options by <tspan fill='green'>your understanding of convexity.</tspan> Please take each question seriously!",
                
                "To begin the formal user study, press the '<tspan fill='red'>Start</tspan>' button."
            ], [
                "You have just finished a group of 9 questions.",
                "You can <tspan fill='green'>take a short break to relax your eyes.</tspan>",
                " ",
                "After the rest, please <tspan fill='red'>finish the next 9 questions without interruption</tspan>.",
                "To continue, press the '<tspan fill='red'>Continue</tspan>' button."
            ], [
                "You have <tspan fill='red'>completed all the questions</tspan>, thank you for your participation!",
                "After the statistics are completed, we will pay the thank-you money one after another.",
                "If you have any questions, please contact: <tspan fill='blue' text-decoration='underline'> <a xlink:href='mailto:jiashu0717c@gmail.com'>jiashu0717c@gmail.com</a></tspan>."
            ]],
            tip_text: [
                // " ",
                "Tip: When the number of categories in a grid layout is large, it may be useful for you",
                "to <tspan fill='green'>check the convexity of more different categories</tspan>."
            ]
        };
    },
    watch: {
        data: function(){
            // console.log('data change', this.data);
            this.layout();
            this.render();
            this.loadHistory();
            this.enableButton();
            Utils.end_loading(500);
        },
        selected: function() {
            this.itemLayout();
            this.itemRender();
            if(this.selected.length < 4) this.enable_next = false;
            else this.enable_next = true;
            this.enableButton();
            this.change_result += 1;
        },
        cur_index: function() {
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
        },
        total_length: function() {
            // update progress
            let pos = this.cur_pos;
            let total = this.total_length[0];
            let state = "(simulation)";
            let delta_x = 1040;
            if(this.cur_pos > total) {
                pos -= total;
                total = this.total_length[1];
                state = "";
                delta_x = 1090
            }
            this.progress.text(`Current progress ${state}: ${pos} / ${total}`)
                .attr('x', delta_x);

            // update button3
            const button3 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 2);
            if(pos == total && total == this.total_length[1]) {
                button3.select("text")
                    .text("Submit");
            }
            else {
                button3.select("text")
                    .text("Next");
            }
        },
        // answer_data: function() {
        //     this.dialogLayout();
        //     this.dialogRender();
        // }
    },
    methods: {
        // authentication
        login: async function(){
            const that = this;
            await axios.post('/api/login', {
            }).then(function(response) {
                console.log('Login user id:', response.data.user_id);
                that.user_id = response.data.user_id;
                that.is_first = response.data.is_first;
                that.is_normal = response.data.is_normal;
                that.finish_all = response.data.finish_all;
            });
        },
        // data fetch functions
        getHackData: function() {
            const that = this;
            axios.post('/api/hack-data', {
            }).then(function(response) {
                // console.log('Get hack data:', response);
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
                    // console.log('Get data:', response.data);
                    that.data = response.data.data;
                    that.history = response.data.history;
                    that.cur_pos = response.data.cur_pos + 1;
                    that.total_length = response.data.total;
                }
            });
        },
        submit: async function() {
            const that = this;
            await axios.post('/api/submit', {
                result: this.selected
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    console.log('Submit error:', response.data.detail);
                    that.$message.error( 'Submit Error:' + response.data.detail);
                }
                else{
                    // console.log('Submit success.');
                    that.$message({
                        message: 'Submit successfully',
                        type: 'success'
                    });
                }
            });
        },
        changeQuestion: async function(nxt) {
            const that = this;
            // console.log(this.is_normal, nxt)
            if(!this.is_normal && nxt == this.total_length[0]) {
                this.breakTime(1);
                this.nxt_index = nxt;
                return;
            }
            if(nxt != this.total_length[0] + this.total_length[1])
                Utils.begin_loading();
            await axios.post('/api/change-question', {
                index: nxt
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    console.log('Change error:', response.data.detail);
                    if(response.data.detail == 'This is the final question.') {
                        that.$message({
                            message: 'Finish all questions successfully!',
                            type: 'success'
                        });
                        that.$alert('<p style="font-size:18px;">You have completed all the questions, thank you for your participation!</p> <br /> \
                            <p style="font-size:18px;">Please <span style="color:red;">click Confirm</span> to fill out the attached questionnaire, we will issue a thank you money later!</p>', 
                            'Congratulations!', {
                            confirmButtonText: 'Confirm',
                            dangerouslyUseHTMLString: true,
                            callback: (action) => {
                                if(action === 'confirm') {
                                    window.open('https://www.wjx.cn/vm/Q03dUrB.aspx#' ,'_blank');
                                    that.breakTime(3);
                                    that.finish_all = true;
                                }
                            }
                        });
                    }
                    else {
                        that.$message({
                            message: response.data.detail,
                            type: 'warning'
                        }); 
                    }
                }
                else{
                    // console.log('Change success.');
                    that.cur_index = nxt;
                }
            });
        },
        loadHistory: function() {
            const history = this.history;
            this.change_result = -1;
            this.repeat_view = true;
            if(history.length === 0) {
                this.repeat_view = false;
                return;
            }
            history.forEach((item) => {
                item.color_id = this.select_colors.indexOf(item.color);
                this.select_state[item.color_id] = true;
                this.svg.selectAll('.grid-group')
                    .filter(e => e.id === this.trans[item.option])
                    .select('.boundary')
                    .attr('stroke', item.color)
                    .attr('opacity', 1);
                this.grids[this.trans[item.option]].selected = true
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
                grid.option = this.options[index];
                const cells = [];
                let i = 0; let j = 0;
                elements.forEach((element, eindex) => {
                    const cell = {};
                    cell.id = eindex;
                    cell.name = `${this.data.index}-${index}-${eindex}`
                    cell.pos = [i, j].concat();
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
            // this.raw_grid = grids[0];
            // this.raw_grid.index = this.data.index;
            this.grids = grids.slice(0);
        },
        itemLayout: function() {
            let divide_size = this.selected.length + 1;
            if(this.selected.length > 0) {
                divide_size += (this.selected.length - 1);
            }
            const item_gap = this.rank_width / divide_size;
            this.items = this.selected.map((op, index) => {
                const item = {};
                item.name = `${this.data.index}-${op.option}-${op.color}`;
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
        dialogLayout: function() {
            const ewidth = (this.dialog_width - 40) / 8;
            const nodes = [];
            const width_size = Math.floor(Math.sqrt(this.grids[0].cells.length));
            for(let i = 0; i < 4; i++){
                const node = {};
                node.id = this.answer_data[0][i];
                node.option = this.trans2[node.id];
                node.name = `answer-${this.data.index}-${node.option}`
                node.x = (2 * i + 1) * ewidth - this.d_grid_width / 2;
                node.y = 45;
                node.width = this.d_grid_width;
                const raw_grid = this.grids[node.id];
                const grid = {};
                grid.id = raw_grid.id;
                grid.width_size = raw_grid.width_size;
                grid.cell_width = raw_grid.cell_width;
                grid.option = raw_grid.option;
                const cells = raw_grid.cells.map((rc) => {
                    const cell = {};
                    cell.id = rc.id;
                    cell.pos = rc.pos.concat();
                    cell.element = rc.element;
                    cell.label = rc.label;
                    cell.color = rc.color;
                    cell.width = this.d_grid_width / width_size;
                    return cell;
                })
                grid.cells = cells;
                grid.name = raw_grid.name;
                node.grid = grid;
                node.color = this.selected.filter(e => e.option == node.option)[0].color;
                node.answer_right = this.selected.length < 4 || node.option == this.selected[i].option;
                nodes.push(node);
            }
            this.dialog_nodes = nodes;
            console.log("ERRR", nodes, this.selected)

            const links = [];
            for(let i = 0; i < 3; i++){
                const link = {};
                link.start = nodes[i];
                link.end = nodes[i+1];
                link.name = `${nodes[i].name}-${nodes[i+1].name}`;
                link.x = (2 * i + 2) * ewidth;
                link.y = 45 + this.d_grid_width / 2;
                link.value = '>';
                links.push(link);
            }
            this.dialog_links = links;

            const xstart = 39;
            const ystart = 365, deltay = 37;
            const rgb = function(rgblist) {
                return `rgb(${rgblist[0]}, ${rgblist[1]}, ${rgblist[2]})`;
            }
            const texts = this.answer_data[1].map((value, index) => {
                value = value.replace(/\[1\]/g, `${nodes[0].option}`);
                value = value.replace(/\[2\]/g, `${nodes[1].option}`);
                value = value.replace(/\[3\]/g, `${nodes[2].option}`);
                value = value.replace(/\[4\]/g, `${nodes[3].option}`);
                value = value.replace(/Category 1/g, `<tspan fill="${rgb(this.tp_colors[0])}">Category 1</tspan>`);
                value = value.replace(/Categories 1/g, `<tspan fill="${rgb(this.tp_colors[0])}" >Categories 1</tspan>`);
                value = value.replace(/blue/g, `<tspan fill="${rgb(this.tp_colors[0])}" >blue</tspan>`);
                value = value.replace(/Category 2/g, `<tspan fill="${rgb(this.tp_colors[1])}" >Category 2</tspan>`);
                value = value.replace(/2, and/g, `<tspan fill="${rgb(this.tp_colors[1])}" >2</tspan>, and`);
                value = value.replace(/red/g, `<tspan fill="${rgb(this.tp_colors[1])}" >red</tspan>`);
                if(this.data.colors[2] !== undefined) {
                    value = value.replace(/Category 3/g, `<tspan fill="${rgb(this.tp_colors[2])}" >Category 3</tspan>`);
                    value = value.replace(/and 3/g, `and <tspan fill="${rgb(this.tp_colors[2])}" >3</tspan>, and`);
                    value = value.replace(/green/g, `<tspan fill="${rgb(this.tp_colors[2])}" >green</tspan>`);
                }
                if(this.data.colors[3] !== undefined) {
                    value = value.replace(/Category 4/g, `<tspan fill="${rgb(this.tp_colors[3])}" >Category 4</tspan>`);
                    value = value.replace(/yellow/g, `<tspan fill="${rgb(this.tp_colors[3])}" >yellow</tspan>`);
                }
                return {
                    value: value,
                    x: xstart,
                    y: ystart + index * deltay
                }
            })
            this.dialog_texts = texts;
        },
        // render functions
        initRender: function() {
            this.svg.attr('width', 1440)
                .attr('height', 1024);
            // background
            this.svg.append('text')
                .text('Judge Convexity of Grid Layouts')
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
                .attr('class', 'inside')
                .text('Sort the following grid layouts by convexity')
                .attr('x', 81)
                .attr('y', 120)
                .attr('font-size', 20);
            this.svg.append('text')
                .attr('class', 'inside')
                .text('in descending order:')
                .attr('x', 81)
                .attr('y', 147)
                .attr('font-size', 20);
            this.progress = this.svg.append('text')
                .attr('class', 'inside')
                .text('Current progress: ')
                .attr('x', 1090)
                .attr('y', 120)
                .attr('font-size', 20);
            // this.svg.append('text')
            //     .text('Raw grid:')
            //     .attr('x', 81)
            //     .attr('y', 292)
            //     .attr('font-size', 20);
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
        gridRender: function(group, animation=true) {
            group.enter()
                .append('rect')
                .attr('class', 'grid-cell')
                .attr('x', d => d.pos[0] * d.width)
                .attr('y', d => d.pos[1] * d.width)
                .attr('width', d => d.width)
                .attr('height', d => d.width)
                .attr('fill', d => `rgb(${d.color[0] * 255},${d.color[1] * 255},${d.color[2] * 255})`)
                .attr('stroke', 'gray')
                .attr('stroke-width', 0.2)
                .attr('opacity', 0)
                .transition()
                .duration(animation ? this.create_duration / 4: 0)
                .delay(animation ? this.remove_duration / 4: 0)
                .attr('opacity', 1);
            group.transition()
                .duration(animation ? this.update_duration: 0)
                .attr('x', d => d.pos[0] * d.width)
                .attr('y', d => d.pos[1] * d.width)
                .attr('width', d => d.width)
                .attr('height', d => d.width)
                .attr('fill', d => `rgb(${d.color[0] * 255},${d.color[1] * 255},${d.color[2] * 255})`)
            group.exit()
                .transition()
                .duration(animation ? this.remove_duration / 4: 0)
                .attr('opacity', 0)
                .remove()
        },
        render: function() {
            // render raw grid
            // const raw_group = this.svg.selectAll('.raw-grid')
            //     .data([this.raw_grid], d => d.index);
            // const raw_create = raw_group.enter()
            //     .append('g')
            //     .attr('class', 'raw-grid')
            //     .attr('transform', 'translate(121, 317)');
            //     // .style('cursor', 'pointer');
            // raw_group.exit()
            //     .transition()
            //     .duration(this.remove_duration)
            //     .attr('opacity', 0)
            //     .remove()
            // let merge_group = raw_group.merge(raw_create);
            // let grid_group = merge_group.selectAll('rect')
            //     .data(d => d.cells, c => c.id);
            // this.gridRender(grid_group);

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
            let merge_group = grids_group.merge(grids_create);
            let grid_group = merge_group.selectAll('.grid-cell')
                .data(d => d.cells, c => c.name);
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
                .duration(this.create_duration / 2)
                .attr('opacity', 1);
            item_group.transition()
                .duration(this.update_duration / 2)
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            item_group.exit()
                .transition()
                .duration(this.remove_duration / 2)
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
                .duration(this.create_duration / 2)
                .attr('opacity', 1);
            link_group.transition()
                .duration(this.update_duration / 2)
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            link_group.select('text')
                .transition()
                .duration(this.update_duration / 2)
                .text(d => d.value);
            link_group.exit()
                .transition()
                .duration(this.remove_duration / 2)
                .attr('opacity', 0)
                .remove();
        },
        dialogRender: function(){
            // render nodes
            const node_drawer = this.d_svg.select('g.answer-nodes');
            const nodes = node_drawer.selectAll('.answer-node')
                .data(this.dialog_nodes, d => d.name);
            const create = nodes.enter()
                .append('g')
                .attr('class', 'answer-node')
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            create.append('rect')
                .attr('class', 'boundary')
                .attr('x', 0)
                .attr('y', 0)
                .attr('width', d => d.width)
                .attr('height', d => d.width)
                .attr('stroke', d => d.answer_right ? 'black': 'red')
                .attr('stroke-width', d => d.answer_right ? 5 : 8)
                .attr('fill', 'None');
            create.append('text')
                .attr('class', 'option-name')
                .text(d => d.option)
                .attr('x', -5)
                .attr('y', -13)
                .attr('font-size', 20)
                .attr('font-weight', d => d.answer_right ? 'normal' :'bold')
                .attr('fill', d => d.answer_right ? 'black': 'red');
            create.append('text')
                .attr('class', 'wrong-answer')
                .attr('x', d => d.width + 14)
                .attr('y', d => d.width + 25)
                .text('▲ Your answer is wrong.')
                .attr('fill', 'red')
                .attr('font-size', 18)
                .attr('opacity', d => d.answer_right ? 0: 1)
                .attr('text-anchor', 'end');
            nodes.select('rect.boundary')
                .transition()
                .duration(this.update_duration / 2)
                .attr('stroke', d => d.answer_right ? 'black': 'red')
                .attr('stroke-width', d => d.answer_right ? 5 : 8);
            nodes.select('text.option-name')
                .transition()
                .duration(this.update_duration / 2)
                .attr('font-weight', d => d.answer_right ? 'normal' :'bold')
                .attr('fill', d => d.answer_right ? 'black': 'red');
            nodes.select('text.wrong-answer')
                .attr('opacity', d => d.answer_right ? 0: 1);
            nodes.exit()
                .attr('opacity', 0)
                .remove();
            const merged_nodes = nodes.merge(create);
            const grids_group = merged_nodes.selectAll('.grid-cell')
                .data(d => d.grid.cells, c => c.id);
            this.gridRender(grids_group, false);
            
            // render links
            this.selected.forEach((d, i, a) => {
                if(i != 0) {
                    if(a[i-1].equal[1] && a[i].equal[0]) {
                        this.dialog_links[i-1].answer_right = false;
                    }
                    else this.dialog_links[i-1].answer_right = true;
                }
            })
            const link_drawer = this.d_svg.select('g.answer-links');
            const links = link_drawer.selectAll('.answer-link')
                .data(this.dialog_links, d => d.names);
            const link_create = links.enter().append('g')
                .attr('class', 'answer-link')
                .attr('transform', d => `translate(${d.x}, ${d.y})`);
            link_create.append('circle')
                .attr('cx', 0)
                .attr('cy', 0)
                .attr('r', 22)
                .attr('stroke', 'rgba(108,108,108, 0.57)')
                .attr('stroke-width', 1)
                .attr('fill', 'rgba(254,250,131,0.73)');
            link_create.append('text')
                .text(d => d.value)
                .attr('x', 0)
                .attr('y', 8)
                .attr('fill', d => d.color)
                .attr('font-size', 22)
                .attr('text-anchor', 'middle')
                .attr('font-weight', 'bold')
                .attr('fill', '#9A9A9A');
            links.select('circle')
                .transition()
                .duration(this.update_duration / 2)
                .attr('stroke', d => d.answer_right ? 'rgba(108,108,108, 0.57)' : 'red')
                .attr('stroke-width', d => d.answer_right ? 1 : 2)
            links.exit()
                .attr('opacity', 0)
                .remove();
            
            // render texts
            // const wrong_num = this.dialog_nodes.filter(d => !d.answer_right).length;
            // let state_str = 'exact';
            // if(wrong_num > 0) state_str = 'partly wrong';
            // if(wrong_num == 4) state_str = 'wrong';
            // let true_str = ' ';
            // this.dialog_nodes.forEach((d, i) => {
            //     if(i != 0) true_str += ' > '
            //     true_str += d.option;
            // })
            // let cur_str = true_str;
            // if(wrong_num > 0) {
            //     let tmp_str = ' ';
            //     this.selected.forEach((d, i, a) => {
            //         if(i != 0) {
            //             if(a[i-1].equal[1] && a[i].equal[0]) {
            //                 tmp_str += ' = '
            //             }
            //             else tmp_str += ' > '
            //         }
            //         tmp_str += d.option;
            //     })
            //     let i = 0, j = 0;
            //     for(i = 0;i < tmp_str.length; i++){
            //         if(tmp_str[i] != cur_str[i]) {
            //             break;
            //         }
            //     }
            //     if(i !== tmp_str.length) {
            //         j = tmp_str.length - 1;
            //         for(;j > -1;j--) {
            //             if(tmp_str[j] != cur_str[j]) {
            //                 break;
            //             }
            //         }
            //         cur_str = tmp_str.slice(0, i) + '<tspan fill="red">' + tmp_str.slice(i,j+1) +'</tspan>' + tmp_str.slice(j+1);
            //     }
            // }

            // const wrong_text = this.d_svg.selectAll('.answer-wrong-text')
            //     .data(['']);
            // wrong_text.enter()
            //     .append('text')
            //     .attr('class', 'answer-wrong-text')
            //     .html(`Your answer is ${state_str}: ${cur_str}.`)
            //     .attr('x', 34)
            //     .attr('y', 315)
            //     .attr('font-size', 22);
            
            // wrong_text.html(`Your answer is ${state_str}: ${cur_str}.`);

            this.d_svg.selectAll('.explain-text')
                .data(['Explanation:'])
                .enter()
                .append('text')
                .attr('class', 'explain-text')
                .text(d => d)
                .attr('x', 34)
                .attr('y', 325)
                .attr('font-size', 22);

            const content = this.d_svg.selectAll('.explain-content')
                .data(this.dialog_texts);
            content.enter()
                .append('text')
                .attr('class', 'explain-content')
                .attr('x', d => d.x)
                .attr('y', d => d.y)
                .html(d => d.value)
                .attr('font-size', 18);
            content.html(d => d.value);
            content.exit()
                .attr('opacity', 0)
                .remove();
        },
        enableButton: function(){
            const button1 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 0);
            if(!this.finish_all && !this.in_break) {
                button1.select('rect').attr('fill', 'rgb(255,255,255)');
                button1.select('text').attr('fill', 'black');
            }
            else {
                button1.select('rect').attr('fill', 'rgba(239,239,239,0.67)');
                button1.select('text').attr('fill', 'rgba(108,108,108,0.72)');
            }
            const button2 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 1);
            if(!this.finish_all && this.data.index > 0) {
                button2.select('rect').attr('fill', 'rgb(255,255,255)');
                button2.select('text').attr('fill', 'black');
            }
            else {
                button2.select('rect').attr('fill', 'rgba(239,239,239,0.67)');
                button2.select('text').attr('fill', 'rgba(108,108,108,0.72)');
            }
            const button3 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 2);
            if(!this.finish_all && this.enable_next) {
                button3.select('rect').attr('fill', 'rgb(255,255,255)');
                button3.select('text').attr('fill', 'black');
            }
            else {
                button3.select('rect').attr('fill', 'rgba(239,239,239,0.67)');
                button3.select('text').attr('fill', 'rgba(108,108,108,0.72)');
            }
            if(!this.finish_all && !this.in_break && this.cur_pos <= this.total_length[0] && this.repeat_view){
                const answer_button = this.svg.selectAll('.answer-button')
                    .data([0]);
                answer_button.enter()
                    .append('text')
                    .text('Answer')
                    .attr('class', 'answer-button')
                    .attr('text-decoration', 'underline')
                    .attr('fill', 'red')
                    .attr('x', 1310)
                    .attr('y', 820)
                    .attr('text-anchor', 'middle')
                    .attr('font-size', 18)
                    .attr('opacity', 0)
                    .style('cursor', 'pointer')
                    .on('click', () => {
                        this.answer_dialog = true;
                    })
                    .transition()
                    .duration(this.create_duration / 2)
                    .attr('opacity', 1);
            }
            else {
                this.svg.selectAll('.answer-button').remove();
            }
        },
        // interaction functions
        highlightButton: function(ev, d) {
            if(this.in_break && d.id == 0) return;
            if((this.data.index == undefined || this.data.index === 0) && d.id == 1) return;
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
            if(this.finish_all) return;
            if(this.in_break && d.id == 0) return;
            if(this.data.index === 0 && d.id == 1) return;
            if(!this.enable_next && d.id == 2) return;
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
            if(this.in_break && d.id == 1) {
                if(this.is_first) return;
                Utils.begin_loading();
                this.workTime();
                return;
            }
            let nxt = this.data.index;
            if(d.id == 1) nxt -= 1;
            else nxt += 1;
            if(this.enable_next && this.change_result > 0) {
                // submit current result
                await this.submit();
                this.change_result = -1;
                if(d.id == 2) {
                    this.nxt_index = nxt;
                    if(this.cur_pos <= this.total_length[0] && !this.repeat_view){
                        this.answer_dialog = true;
                        return;
                    }
                    if(!this.in_break && (this.cur_pos - this.total_length[0]) % 9 == 0
                        && this.cur_pos != this.total_length[0] + this.total_length[1]
                        && this.cur_pos > this.total_length[0]) {
                        this.breakTime(2);
                        return;
                    }
                }
            }
            await this.changeQuestion(nxt);
        },
        openDialog: async function() {
            const that = this;
            await axios.post('/api/get-answer', {
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    // console.log('Get answer error:', response.data.detail);
                    this.answer_dialog = false;
                }
                else{
                    // console.log('Get Answer', response.data);
                    that.answer_data = response.data.answer;
                    that.dialogLayout();
                    that.dialogRender();
                }
            });
            // console.log("get answer await")
        },
        closeDialog: function() {
            if(!this.repeat_view) this.changeQuestion(this.nxt_index);
            // if(this.cur_pos < this.total_length[0])
            //     this.changeQuestion(this.nxt_index);
            // else {
            //     const that = this;
            //     this.$alert('<p style="font-size:17px;">Next, you will enter the <span style="color:red;">formal answering session</span>. Please take each question seriously!</p><br/>\
            //                  <p style="font-size:14px;">Tip: When the number of categories is large, it may be useful for you to <span style="color:green;">check more results of different areas.</span></p>', 'Attention please!', {
            //                 confirmButtonText: 'Confirm',
            //                 dangerouslyUseHTMLString: true,
            //                 callback: () => {
            //                     that.changeQuestion(that.nxt_index);
            //                 }
            //     });
            //     // this.breakTime();
            // }
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
        },
        startQuestions: function() {
            if(this.consent_result.agree1 && this.consent_result.agree2 
                && this.consent_result.agree3 && this.consent_result.agree4) {
                    this.consent_form = false;
                }
            else {
                this.$alert('<p style="font-size:18px;">Please read the consent form first and <span style="color:red;">agree to the relevant options</span>.</p>', 'Attention', {
                    confirmButtonText: 'Confirm',
                    dangerouslyUseHTMLString: true,
                });
            }
        },
        closeTutorial: function() {
            const that = this;
            this.$confirm('<p style="font-size:18px;">Have you finished the tutorial? </p>\
                <p style="font-size:18px;"><span style="color:red;">You can\'t return to the video after closing. </span></p>', 'Attention', {
                confirmButtonText: 'Confirm',
                cancelButtonText: 'Cancel',
                dangerouslyUseHTMLString: true,
                type: 'warning'
            }).then(() => {
                that.tutorial = false;
            });
        },
        // appended page
        breakTime: function(use_text=0) {
            // clear svg
            this.grids.forEach((grid) => {
                    grid.selected = false;
                });
            this.cur_select = 0;
            this.selected = [];
            this.select_state = [false, false, false, false];
            this.svg.selectAll('.grid-group')
                .select('.boundary')
                .attr('opacity', 0);
            d3.selectAll(".grid-group")
                .remove();
            // show table
            let used_text = [];
            used_text = this.break_text[use_text];
            // console.log(use_text, this.break_text[use_text])
            let start_y = use_text == 0 ? 350: 220;
            if(use_text == 2) start_y = 310;
            if(use_text == 3) start_y = 400;
            let button_y = use_text != 1? 620: 700;
            if(use_text == 0) button_y = 580;
            const str_data = used_text.map((d, index) => {
                return {
                    id: index,
                    value: d,
                    x: 700,
                    y: start_y + 40 * index
            }});
            // show text
            const table_svg = this.svg.append('g')
                .attr('class', 'table-svg')
            const that = this;
            table_svg.selectAll('.break-text')
                .data(str_data)
                .enter()
                .append('text')
                .attr('class', 'break-text')
                .html(d => d.value)
                .attr('x', d => d.x)
                .attr('y', d => d.y)
                .attr('font-size', 25)
                // .attr('font-weight', 'bold')
                .attr('text-anchor', 'middle')
                .attr('opacity', 0)
                .transition()
                .duration(this.create_duration)
                .attr('opacity', 1)
            if(use_text == 1) {
                const tip_data = this.tip_text.map((d, index) => {
                    return {
                        id: index,
                        value: d,
                        x: 700,
                        y: 560 + 35 * index
                }});
                table_svg.selectAll('.tip-text')
                    .data(tip_data)
                    .enter()
                    .append('text')
                    .attr('class', 'tip-text')
                    .html(d => d.value)
                    .attr('x', d => d.x)
                    .attr('y', d => d.y)
                    .attr('font-size', 23)
                    // .attr('font-weight', 'bold')
                    .attr('text-anchor', 'middle')
                    .attr('opacity', 0)
                    .transition()
                    .duration(this.create_duration)
                    .attr('opacity', 1)
            }
            // show button
            if(use_text != 3) {
                table_svg.append('g')
                    .attr('class', 'break-button')
                    .attr('transform', `translate(700, ${button_y})`)
                    .style('cursor', 'pointer')
                    .on('mouseover', () => {
                        table_svg.select('g.break-button')
                            .select('rect')
                            .attr('stroke', 'blue');
                    })
                    .on('mouseout', () => {
                        table_svg.select('g.break-button')
                            .select('rect')
                            .attr('stroke', 'rgb(187,187,187)');
                    })
                    .on('click', () => {
                        // that.$message({
                        //         message: '功能测试中，请等待后续发布',
                        //         type: 'warning'
                        //     }); 
                        Utils.begin_loading();
                        that.workTime(use_text);
                    })
                    .attr('opacity', 0)
                    .transition()
                    .duration(this.create_duration)
                    .attr('opacity', 1);
                table_svg.select('g.break-button')
                    .append('rect')
                    .attr('x', -80)
                    .attr('y', -20)
                    .attr('width', 160)
                    .attr('height', 40)
                    .attr('stroke', 'rgb(187,187,187)')
                    .attr('stroke-width', 2)
                    .attr('fill', 'red')
                table_svg.select('g.break-button')
                    .append('text')
                    .text(use_text < 2 ? 'Start': 'Continue')
                    .attr('x', 0)
                    .attr('y', 7)
                    .attr('font-size', 22)
                    .attr('font-weight', 'bold')
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'white')
            }
            this.svg.selectAll('text.inside')
                .attr('opacity', 0)
            // change state
            this.in_break = true;
        },
        workTime: function(type=0) {
            // delete table
            this.svg.select('g.table-svg')
                .transition()
                .duration(this.remove_duration)
                .attr('opacity', 0)
                .remove();
            this.svg.selectAll('text.inside')
                .attr('opacity', 1)
            this.in_break = false;
            // console.log(this.nxt_index)
            if(type == 0) {
                this.getData();
                return;
            }
            if(type == 1) {
                this.is_normal = true;
            }
            this.changeQuestion(this.nxt_index);
        }
    },
    async mounted() {
        await this.login();
        this.initRender();
        if(this.is_first) {
            this.breakTime();
            this.enableButton();
            this.consent_form = true;
            this.tutorial = true;
            return;
        }
        if(this.finish_all) {
            this.breakTime(3);
            this.enableButton();
            return;
        }
        // this.getHackData();
        this.getData();
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

.form {
    font-family: Times, "Times New Roman", "楷体";
}

.form button span {
    font-family: Times, "Times New Roman", "楷体";
}

.form .el-dialog__title {
    font-size: 25px;
}

.form .el-checkbox__label {
    font-size: 20px;
}

.item label {
    font-size: 20px;
    word-break: keep-all;
    word-wrap: break-word;
}

#sheet-link {
    color: rgb(64,158,255);
    text-decoration: underline;
    cursor: pointer;
}

#sheet p {
    text-anchor: start;
    text-align: left;
    font-size: 18px;
    word-break: keep-all;
    word-wrap: break-word;
}

#sheet .el-dialog__body {
    padding-top: 5px;
}

#consent .el-dialog__body {
    padding-top: 15px;
}

</style>