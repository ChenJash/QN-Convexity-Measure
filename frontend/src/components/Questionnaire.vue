<template>
  <div class="question-naire">
    <el-dialog title="教程" :visible.sync="tutorial" width="1300px" class="form" :before-close="closeTutorial">
        <video width="1250" height="630" controls id="tutorial">
            <source src="../assets/mp4/tutorial.mp4" />
        </video>
    </el-dialog>
    <el-dialog title="知情同意书" :visible.sync="consent_form" width="1100px" :show-close="false" 
            :close-on-press-escape="false" :close-on-click-modal="false" class="form" id="consent">
        
        <el-form label-position="left" label-width="1000px" :model="consent_result">
        <el-form-item class="item">
            <template slot="label">1.	  本人确认已于2023年2月15日阅读并了解了该项目<span id="sheet-link" @click="info_sheet=true">相关研究信息</span> ，并已从项目负责人处得到考虑、提问的机会，且得到满意答复。  </template>
            <el-checkbox v-model="consent_result.agree1">同意</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="2.	本人知晓对该项目的参与为自愿，且可以随时退出，无需任何理由，同时权利不会受任何影响。">
            <el-checkbox v-model="consent_result.agree2">同意</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="3.	本人知晓可随时要求获取或销毁所提供的个人信息。">
            <el-checkbox v-model="consent_result.agree3">同意</el-checkbox>
        </el-form-item>
        <el-form-item class="item" label="4.	本人同意参加此项研究。">
            <el-checkbox v-model="consent_result.agree4">同意</el-checkbox>
        </el-form-item>
        <el-button type="primary" @click="startQuestions">确定</el-button>
        </el-form>
    </el-dialog>
    <el-dialog title="参与者须知" :visible.sync="info_sheet" width="1300px" class="form" id="sheet">
        <p>您正在被邀请参加一项研究。 在您决定是否参与之前，了解为什么要进行研究以及研究将涉及什么对您来说很重要。 请花时间仔细阅读以下信息，如果您需要更多信息或有任何不明白之处，请随时询问我们。 也请随时与您的朋友、亲戚以及您希望的任何其他人讨论此事。 我们想强调的是，研究并非强制性的，只有在您愿意的情况下才应同意参加。</p>
        <p>该研究的目的是开发一种网格布局方法，以更好地保留集类簇结构。 根据格式塔原则，人们对于凸形状的感知优于凹图形， 因此我们希望生成使每个簇更凸的布局结果。 这个过程需要一个凸性度量，然而，目前在网格布局中还没有普遍接受的凸度度量。我们想知道哪种度量更符合人类的感知，为此，我们需要让参与者像您一样看到一组网格布局结果，然后根据凸性对结果进行排序。</p>
        <p>当您执行任务时，您与系统的交互将在安全的环境中进行。 研究人员将始终在一旁观察和回答您可能遇到的任何问题和疑虑，并确保所有事情都按预期进行，并且您始终感到舒适和安全。</p>
        <p>系统会自动记录您的排序结果以供日后分析。 此外，您可能会被要求完成一些简单的问卷调查，并回答一些关于您对比较不同网格布局的凸度的一般经验和感受的问题。 这些问题不会询问您的任何个人信息，如果您对任何问题感到不舒服，您选择不回答也没关系。 用户研究将持续约 1 小时。</p>
        <p>收集的数据将帮助我们了解如何设计更好的网格布局算法来保持类簇形状的凸性，并使我们能够撰写报告并将其作为学术论文发表。 如果发表任何报告和论文，它们将不会包含任何可用于识别参与我们实验的任何参与者的信息。</p>
        <p>其他参与者可能是 THU 和 XJTLU 的学生以及他们的熟人。 您和其他参与者将获得的好处之一是体验最先进的技术，例如可视化、网格布局和凸度测量。</p>
        <p>我们想向所有参与者表明，他们不是被测试的人，我们只是在评估对凸性的看法。 您的参与完全是自愿的，您可以随时停止。</p>
        <p>如果您不满意或有任何问题，请随时联系俞凌云老师，我们将尽力提供帮助。 如果您仍然不满意或有您觉得不能来找我们的投诉，那么您可以通过 <a href="mailto:ethics@xjtlu.edu.cn">ethics@xjtlu.edu.cn</a> 联系研究伦理小组委员会主席，并提供足够的详细信息以帮助确定项目。</p>
    </el-dialog>
    <svg id="main-svg">
    </svg>
    <el-dialog title="习题解答" :visible.sync="answer_dialog" width="1300px" @open="openDialog" @closed="closeDialog" class="form">
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
            extra: true,
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
            // select_colors: ['#DE0707', '#0F40F5', '#A16222', '#81B337'], 
            select_colors: ['#AAA7BC', '#AAA7BC', '#AAA7BC', '#AAA7BC'],
            select_state: [false, false, false, false],
            buttons: [{
                id: 0,
                text: '清空作答',
                y: 973
            }, {
                id: 1,
                text: '上一题',
                y: 919
            }, {
                id: 2,
                text: '下一题',
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
                "现在，有6道模拟测试题供您练习。练习题中没有任何时间要求。",
                "请您使用电脑或平板作答，显示屏过小可能会影响查看与作答。",
                "每道练习题被作答后，我们会为您展示题目的正确答案和对应的解释。",
                "如果您已准备就绪，请点击 <tspan fill='red'>“开始”</tspan> 按钮, 进入<tspan fill='red'>模拟测试</tspan>。"
            ],[
                "接下来，您将进入<tspan fill='red'>正式作答环节</tspan>。总共包含36道题目，平均分为4组。",
                "在完成每一组的作答后，您都可以稍做休息，再继续进行下一组的作答。",
                "但是，请确保您在每一组的作答中<tspan fill='red'>不间断地完成组内的所有问题</tspan>。",
                "",
                "正式作答中，您遇到的题目会比模拟测试的题目更加困难。",
                "每一个问题可能没有标准答案，每一个选项都具有相对不差的凸性。",
                "按照自己<tspan fill='green'>对于凸性的理解</tspan>进行排序即可， 请您务必认真对待每一道题!", 
                "如果您已准备就绪，请点击 <tspan fill='red'>“开始”</tspan> 按钮, 进入<tspan fill='red'>正式作答</tspan>。"
            ], [
                "您刚刚完成了一组 10 道题目。",
                "您可以<tspan fill='green'>稍作休息，放松一下自己的眼睛</tspan>。",
                " ",
                "充分休息后，请您<tspan fill='red'>不间断地完成下一组的所有题目</tspan>。",
                "如果您已准备就绪，请点击 <tspan fill='red'>“继续”</tspan> 按钮进入作答。"
            ], [
                "您已完成<tspan fill='red'>全部问题的作答</tspan>, 衷心感谢您的再次参与！",
                // "在信息统计完成后，我们将会陆续发放答谢金！",
                "如果您有与本次调研相关的问题，请联系：<tspan fill='blue' text-decoration='underline'> <a xlink:href='mailto:jiashu0717c@gmail.com'>jiashu0717c@gmail.com</a></tspan>."
            ],[
                "接下来，您将进入补充题目<tspan fill='red'>正式作答</tspan>。共包含20道题目，平均分为2组。",
                "在完成每一组的作答后，您都可以稍做休息，再继续进行下一组的作答。",
                "但是，请确保您在每一组的作答中<tspan fill='red'>不间断地完成组内的所有问题</tspan>。",
                "",
                "正式作答中，您遇到的题目会比模拟测试的题目更加困难。",
                "每一个问题可能没有标准答案，每一个选项都具有相对不差的凸性。",
                "按照自己<tspan fill='green'>对于凸性的理解</tspan>进行排序即可， 请您务必认真对待每一道题!", 
                "如果您已准备就绪，请点击 <tspan fill='red'>“开始”</tspan> 按钮, 进入<tspan fill='red'>正式作答</tspan>。"
            ]],
            tip_text: [
                "小提示： 当网格布局较为相似时，尝试<tspan fill='green'>观察更多的细节</tspan>，",
                "或者 <tspan fill='green'>使用 “=” 号</tspan> 表达你认为它们非常相似相似、难以辨认。",
                // "Tip: When the number of categories in a grid layout is large, it may be useful for you",
                // "to <tspan fill='green'>check the convexity of more different categories</tspan>."
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
            let state = "(模拟测试) ";
            let delta_x = 1090;
            if(this.cur_pos > total) {
                pos -= total;
                total = this.total_length[1];
                state = "";
                delta_x = 1170
            }
            this.progress.text(`当前进度 ${state}:  ${" "} ${pos} / ${total}`)
                .attr('x', delta_x)

            // update button3
            const button3 = this.svg.selectAll('.qn-buttons').filter(d => d.id === 2);
            if(pos == total && total == this.total_length[1]) {
                button3.select("text")
                    .text("提交");
            }
            else {
                button3.select("text")
                    .text("下一题");
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
                        message: '提交成功！',
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
                            message: '你已完成全部作答！',
                            type: 'success'
                        });
                        that.$alert('<p style="font-size:18px;">您已完成全部问题的作答，衷心感谢您的参与</p> <br /> \
                            <p style="font-size:18px;">请您<span style="color:red;">点击“确认”按钮</span> 填写附加问卷，我们将在后续发放感谢金!</p>', 
                            '恭喜!', {
                            confirmButtonText: '确认',
                            dangerouslyUseHTMLString: true,
                            callback: (action) => {
                                if(action === 'confirm') {
                                    // window.open('https://www.wjx.cn/vm/maNPK0B.aspx#' ,'_blank');
                                    window.open('https://www.wjx.cn/vm/eYvyA3X.aspx#' ,'_blank'); 
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
                node.index = i;
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

            const xstart = 72;
            const ystart = 365, deltay = 37;
            const rgb = function(rgblist) {
                return `rgb(${rgblist[0]}, ${rgblist[1]}, ${rgblist[2]})`;
            }
            const texts = this.answer_data[1].map((value, index) => {
                value = value.replace(/\[1\]/g, `${nodes[0].option}`);
                value = value.replace(/\[2\]/g, `${nodes[1].option}`);
                value = value.replace(/\[3\]/g, `${nodes[2].option}`);
                value = value.replace(/\[4\]/g, `${nodes[3].option}`);
                value = value.replace(/类别 1/g, `<tspan fill="${rgb(this.tp_colors[0])}">类别 1</tspan>`);
                value = value.replace(/类别 1/g, `<tspan fill="${rgb(this.tp_colors[0])}" >类别 1</tspan>`);
                value = value.replace(/蓝色/g, `<tspan fill="${rgb(this.tp_colors[0])}" >蓝色</tspan>`);
                value = value.replace(/类别 2/g, `<tspan fill="${rgb(this.tp_colors[1])}" >类别 2</tspan>`);
                value = value.replace(/2 和/g, `<tspan fill="${rgb(this.tp_colors[1])}" >2</tspan> 和`);
                value = value.replace(/红色/g, `<tspan fill="${rgb(this.tp_colors[1])}" >红色</tspan>`);
                value = value.replace(/、2/g, `、<tspan fill="${rgb(this.tp_colors[1])}" >2</tspan>`);
                if(this.data.colors[2] !== undefined) {
                    value = value.replace(/类别 3/g, `<tspan fill="${rgb(this.tp_colors[2])}" >类别 3</tspan>`);
                    value = value.replace(/和 3/g, `和 <tspan fill="${rgb(this.tp_colors[2])}" >3</tspan>`);
                    value = value.replace(/绿色/g, `<tspan fill="${rgb(this.tp_colors[2])}" >绿色</tspan>`);
                }
                if(this.data.colors[3] !== undefined) {
                    value = value.replace(/类别 4/g, `<tspan fill="${rgb(this.tp_colors[3])}" >类别 4</tspan>`);
                    value = value.replace(/黄色/g, `<tspan fill="${rgb(this.tp_colors[3])}" >黄色</tspan>`);
                    value = value.replace(/、4/g, `、<tspan fill="${rgb(this.tp_colors[3])}" >4</tspan>`);
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
                .text('网格布局中的凸性')
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
                .attr('font-weight', 'bold')
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
                .text('请根据凸性从好到差的顺序')
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
                .attr('x', 81)
                .attr('y', 120)
                .attr('font-size', 20);
            this.svg.append('text')
                .attr('class', 'inside')
                .text('排列以下网格布局：')
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
                .attr('x', 81)
                .attr('y', 147)
                .attr('font-size', 20);
            this.progress = this.svg.append('text')
                .attr('class', 'inside')
                .text('当前进度: ')
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
                .attr('xml:space', 'preserve')
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
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
                .attr('stroke', 'white')
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
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
                .attr('stroke-width', 2.5)
                .attr('width', 134)
                .attr('height', 46)
                .attr('fill', 'white');
            item_create.append('text')
                .text(d => d.option)
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
                .attr('x', -4)
                .attr('y', -4)
                .attr('width', d => d.width+8)
                .attr('height', d => d.width+8)
                .attr('stroke', d => d.answer_right ? 'green': 'red')
                .attr('stroke-width', d => d.answer_right ? 2: 2)
                .attr('fill', 'None');
            create.append('text')
                .attr('class', 'option-name')
                .text(d => d.option)
                .attr('x', -5)
                .attr('y', -13)
                .attr('font-size', 20)
                .attr('font-weight', d => d.answer_right ? 'normal' :'bold')
                .attr('fill', d => d.answer_right ? 'green': 'red');
            create.append('text')
                .attr('class', 'wrong-answer')
                .attr('x', d => d.width + 14)
                .attr('y', d => d.width + 25)
                .text('▲ 您的答案不正确')
                .attr('fill', 'red')
                .attr('font-size', 18)
                .attr('opacity', d => d.answer_right ? 0: 1)
                .attr('text-anchor', 'end');

            nodes.select('rect.boundary')
                .transition()
                .duration(this.update_duration / 2)
                .attr('stroke', d => d.answer_right ? 'green': 'red')
                .attr('stroke-width', d => d.answer_right ? 2 : 2);
            nodes.select('text.option-name')
                .transition()
                .duration(this.update_duration / 2)
                .attr('font-weight', d => d.answer_right ? 'normal' :'bold')
                .attr('fill', d => d.answer_right ? 'green': 'red');
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
                .attr('stroke', d => d.answer_right ? 'rgba(108,108,108, 0.57)' : 'red')
                .attr('stroke-width', d => d.answer_right ? 1 : 2)
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
            //         }length
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
            //     .data(['解析：']);
            // wrong_text.enter()
            //     .append('text')
            //     .attr('class', 'answer-wrong-text')
            //     .html(`Your answer is ${state_str}: ${cur_str}.`)
            //     .attr('x', 34)
            //     .attr('y', 315)
            //     .attr('font-size', 22);
            
            // wrong_text.html(`Your answer is ${state_str}: ${cur_str}.`);

            this.d_svg.selectAll('.explain-text')
                .data(['解析:'])
                .enter()
                .append('text')
                .attr('class', 'explain-text')
                .text(d => d)
                .attr('x', 50)
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
                .attr('font-size', 20);
            content.html(d => d.value);
            content.exit()
                .attr('opacity', 0)
                .remove();
            
            // render marks
            const mark_id = parseInt(this.data.question_name.split("-")[1]);
            this.marksRender(mark_id);
        },
        marksRender: function(mark_id){
            const nodes = this.d_svg.select('g.answer-nodes').selectAll('.answer-node');
            const ewidth = this.d_grid_width / 20;
            const pos = function(i, j) {
                return `${j*ewidth},${i*ewidth}`;
            };
            const getLine = function(nodes) {
                console.assert(nodes.length > 1);
                let str = 'M ';
                str += pos(nodes[0][0], nodes[0][1]);
                for(let i = 1; i < nodes.length; i++) {
                    str += 'L ';
                    str += pos(nodes[i][0], nodes[i][1]);
                }
                return str;
            }
            const drawLine = function(grid, nodes) {
                grid.append('path')
                    .attr('d', getLine(nodes))
                    .attr('stroke', 'red')
                    .attr('stroke-width', 1)
                    .attr('fill', 'none');
            }
            const _getLine = function(nodes) {
                console.assert(nodes.length > 1);
                let str = 'M ';
                str += pos(nodes[0][1], nodes[0][0]);
                for(let i = 1; i < nodes.length; i++) {
                    str += 'L ';
                    str += pos(nodes[i][1], nodes[i][0]);
                }
                return str;
            }
            const _drawLine = function(grid, nodes) {
                grid.append('path')
                    .attr('d', _getLine(nodes))
                    .attr('stroke', 'red')
                    .attr('stroke-width', 1)
                    .attr('fill', 'none');
            }
            if(mark_id == 0) {
                const grid1 = nodes.filter(d => d.index == 0);
                drawLine(grid1, [[4,4], [5,4], [5,5]]);
                drawLine(grid1, [[6,7], [7,7], [7,8]]);
                drawLine(grid1, [[7,9], [8,9], [8,10]]);
                drawLine(grid1, [[13,10], [13,11], [12,11]]);
                const grid2 = nodes.filter(d => d.index == 1);
                drawLine(grid2, [[3,2], [4,2], [4,3]]);
                drawLine(grid2, [[4,4], [5,4], [5,5]]);
                drawLine(grid2, [[5,6], [6,6], [6,7]]);
                drawLine(grid2, [[6,9], [6,10], [7,10], [7,11], [8,11]]);
                drawLine(grid2, [[10,11], [11,11], [11,12]]);
                drawLine(grid2, [[10,14], [9,14], [9,16], [10,16], [10, 17]]);
                const grid3 = nodes.filter(d => d.index == 2);
                drawLine(grid3, [[3,2], [4,2], [4,3]]);
                drawLine(grid3, [[4,4], [5,4], [5,5]]);
                drawLine(grid3, [[5,6], [6,6], [6,7]]);
                // drawLine(grid3, [[6,8], [6,9], [5,9], [5,10]]);
                // drawLine(grid3, [[5,11], [5,12], [7,12], [7,11]]);
                drawLine(grid3, [[9,11], [9,10], [10,10]]);
                drawLine(grid3, [[13,10], [14,10], [14,9]]);
                drawLine(grid3, [[12,11], [12,12], [11,12]]);
                // drawLine(grid3, [[10,14], [9,14], [9,15]]);
                // drawLine(grid3, [[9,16], [9,17],[10,17], [10, 19], [11,19]]);
                drawLine(grid3, [[4, 8],[8,8], [8, 13], [4,13], [4,8]]);
                drawLine(grid3, [[8.5, 12],[8.5,19], [13, 19], [13,12], [8.5,12]]);
                const grid4 = nodes.filter(d => d.index == 3);
                drawLine(grid4, [[3,2], [4,2], [4,3]]);
                drawLine(grid4, [[4,4], [5,4], [5,5]]);
                drawLine(grid4, [[5,6], [6,6], [6,7]]);
                // drawLine(grid4, [[6,7], [6,8], [4,8], [4,9], [3,9], [3,10], [4,10], [4,13], [6,13], [6,12]]);
                drawLine(grid4, [[12,8], [12,7], [11,7], [11,8]]);
                drawLine(grid4, [[13,9], [13,10], [14,10], [14,9]]);
                drawLine(grid4, [[12,11], [12,12], [11,12]]);
                // drawLine(grid4, [[9,16], [10,16],[10,18], [9, 18], [9,19], [11, 19]]);
                drawLine(grid4, [[2, 7],[7,7], [7, 14], [2,14], [2,7]]);
                drawLine(grid4, [[7.5, 12],[7.5,19.5], [13, 19.5], [13,12], [7.5,12]]);
            }
            if(mark_id == 1) {
                const grid1 = nodes.filter(d => d.index == 0);
                _drawLine(grid1, [[11,9], [11,10], [12,10]]);
                _drawLine(grid1, [[14,13], [14,15], [16,15]]);
                _drawLine(grid1, [[16,16], [16,18], [18,18]]);
                const grid2 = nodes.filter(d => d.index == 1);
                _drawLine(grid2, [[2,8], [2,9], [4,9], [4,8], [8,8], [8,10],[9,10]]);
                _drawLine(grid2, [[12,10], [14,10], [14,9], [13,9]]);
                _drawLine(grid2, [[18,1],[18,2], [17,2]]);
                _drawLine(grid2, [[14,13],[14,14], [15,14]]);
                _drawLine(grid2, [[16,2],[15,2], [15,3], [14,3]]);
                _drawLine(grid2, [[16,16], [16,18], [18,18]]);
                const grid3 = nodes.filter(d => d.index == 2);
                _drawLine(grid3, [[1,7], [1,8], [2,8], [2,10], [4,10], [4,8], [5,8], [5,6], [7,6],[7,7],[8,7],[8,10]]);
                _drawLine(grid3, [[12,10], [14,10], [14,9], [13,9], [13,8]]);
                _drawLine(grid3, [[17,1], [17,3], [16,3], [16,4], [15,4], [15,2], [14,2], [14,3],[13,3],[13,4]]);
                _drawLine(grid3, [[16,16], [16,18], [18,18]]);
                _drawLine(grid3, [[13,12], [13,13], [14,13]]);
                const grid4 = nodes.filter(d => d.index == 3);
                _drawLine(grid4, [[1,6], [1,8], [2,8], [2,11], [5,11], [5,10], [4,10], [4,8], [5,8], [5,7],[6,7],[6,4],[7,4],[7,8],[8,8],[8,12],[9,12],[9,13],[10,13],[10,11]]);
                _drawLine(grid4, [[17,1], [17,3], [16,3], [16,4], [15,4], [15,2], [13,2], [13,3],[12,3],[12,4],[11,4],[11,5],[14,5],[14,6],[13,6]]);
                _drawLine(grid4, [[12,9], [14,9], [14,10],[12,10]]);
                _drawLine(grid4, [[14,13], [15,13], [15,12], [16,12],[16,13],[18,13],[18,14],[17,14],[17,15],[16,15],[16,16],[15,16],[15,17],[16,17],[16,18],[18,18]]);
            }
            if(mark_id == 2) {
                const grid1 = nodes.filter(d => d.index == 0);
                drawLine(grid1, [[2,1], [2,2], [3,2]]);
                drawLine(grid1, [[5,5], [6,5], [6,6]]);
                drawLine(grid1, [[16,18], [17,18], [17,19]]);
                const grid2 = nodes.filter(d => d.index == 1);
                drawLine(grid2, [[3,2], [3,3], [4,3]]);
                drawLine(grid2, [[5,5], [6,5], [6,6]]);
                drawLine(grid2, [[6,8], [7,8], [7,9]]);
                drawLine(grid2, [[7,12], [7,13], [8,13], [8,12]]);
                drawLine(grid2, [[14,15], [15,15], [15,16]]);
                drawLine(grid2, [[16,17], [17,17], [17,18]]);
                const grid3 = nodes.filter(d => d.index == 2);
                drawLine(grid3, [[3,2], [3,3], [4,3]]);
                drawLine(grid3, [[5,6], [6,6], [6,8],[5,8],[5,10],[6,10], [6,11],[8,11],[8,9],[9,9],[9,11],[10,11],[10,13]]);
                drawLine(grid3, [[14, 14],[15,14], [15,15], [16,15],[16,16],[17,16],[17,18], [16,18], [16,19], [15,19]]);
                const grid4 = nodes.filter(d => d.index == 3);
                drawLine(grid4, [[3,2], [3,4], [4,4], [4,3]]);
                drawLine(grid4, [[6,6] , [6,8],[5,8],[5,9],[4,9],[4,10],[5,10],[5,11],[6,11],[6,13],[7,13],[7,10],[8,10],[8,7],[9,7],[9,11],[10,11],[10,14]]);
                drawLine(grid4, [[14, 14],[15,14], [15,16], [18,16],[18,17],[17,17],[17,18], [16,18], [16,19], [15,19]]);
            }
            if(mark_id == 3) {
                const grid2 = nodes.filter(d => d.index == 1);
                drawLine(grid2, [[10,4], [10,5], [9,5]]);
                drawLine(grid2, [[9,8], [9,9], [10,9]]);
                drawLine(grid2, [[11,9], [12,9], [12,10]]);
                drawLine(grid2, [[12,13], [12,14], [11,14]]);
                drawLine(grid2, [[9,14], [8,14], [8,15]]);
                drawLine(grid2, [[8,16], [8,17], [10,17], [10,18]]);
                const grid3 = nodes.filter(d => d.index == 2);
                drawLine(grid3, [[6,0],[10, 2], [12, 4], [6,6], [15, 12], [6,16],[12,20]]);
                // drawLine(grid3, [[10, 2],[10, 16], [16, 16], [16, 2],[10, 2]]);
                const grid4 = nodes.filter(d => d.index == 3);
                drawLine(grid4, [[6,0],[10, 2], [12, 4], [6,6], [18, 12], [3,16],[14,20]]);
            }
            if(mark_id == 4) {
                const grid1 = nodes.filter(d => d.index == 0);
                _drawLine(grid1, [[5,8], [7,8], [7,10]]);
                _drawLine(grid1, [[7,15], [7,16], [6,16]]);
                _drawLine(grid1, [[12,12], [12,14], [10,14]]);
                const grid2 = nodes.filter(d => d.index == 1);
                _drawLine(grid2, [[9,1], [9,2], [11,2], [11,3]]);
                _drawLine(grid2, [[11,5], [11,6], [12,6]]);
                _drawLine(grid2, [[1,8], [2,8], [2,9],[3,9]]);
                _drawLine(grid2, [[1,16], [2,16], [2,17],[3,17]]);
                _drawLine(grid2, [[5,9], [7,9], [7,11]]);
                _drawLine(grid2, [[8,16], [9,16], [9,15]]);
                _drawLine(grid2, [[12,13], [12,14], [11,14]]);
                _drawLine(grid2, [[17,8], [18,8], [18,7],[19,7]]);
                const grid3 = nodes.filter(d => d.index == 2);
                _drawLine(grid3, [[1,8], [2,8], [2,9],[3,9]]);
                _drawLine(grid3, [[1,16], [3,16], [3,17],[4,17]]);
                _drawLine(grid3, [[7,17], [8,17], [8,16],[7,16]]);
                _drawLine(grid3, [[9,14], [10,14], [10,13]]);
                _drawLine(grid3, [[19,7], [19,8], [18,8]]);
                _drawLine(grid3, [[17,8], [17,9], [16,9]]);
                _drawLine(grid3, [[9,1], [9,2], [10,2]]);
                _drawLine(grid3, [[13,10], [13,11], [12,11]]);
                _drawLine(grid3, [[13,10], [13,9], [14,9]]);
                _drawLine(grid2, [[5,9], [7,9], [7,11]]);
                _drawLine(grid3, [[10,4], [10,5], [11,5]]);
                _drawLine(grid3, [[12,6], [12,7], [13,7]]);
                _drawLine(grid3, [[15,7], [15,8], [16,8]]);
                const grid4 = nodes.filter(d => d.index == 3);
                _drawLine(grid4, [[1,6], [1,8], [4.5,10], [6.5,7], [9,9.5],[6,13.5],[8,17],[10,17],[8,14.5],[13,10]]);
                _drawLine(grid4, [[1,14], [5,18], [8,17]]);
                _drawLine(grid4, [[10,2], [12,3.5], [10,4.5], [10,4.5],[12,7]]);
            }
            if(mark_id == 5) {
                const grid1 = nodes.filter(d => d.index == 0);
                drawLine(grid1, [[11,15], [11,16], [10,16]]);
                const grid2 = nodes.filter(d => d.index == 1);
                drawLine(grid2, [[8, 2], [9,2], [9,3]]);
                drawLine(grid2, [[11, 4], [12,4], [12,5]]);
                drawLine(grid2, [[14, 7], [15,7], [15,8]]);
                drawLine(grid2, [[16, 9], [17,9], [17,10]]);
                drawLine(grid2, [[18, 11], [18,12], [19,12]]);
                drawLine(grid2, [[15, 11], [15,12], [14,12]]);
                drawLine(grid2, [[13, 12], [13,13], [12,13]]);
                drawLine(grid2, [[9, 15], [9,16], [8,16]]);
                drawLine(grid2, [[5, 15], [6, 15], [6,16]]);
                drawLine(grid2, [[4, 13], [5, 13], [5,14]]);
                drawLine(grid2, [[3, 11], [4, 11], [4,12]]);
                drawLine(grid2, [[1,10], [1, 9], [2, 9], [2,10]]);
                const grid3 = nodes.filter(d => d.index == 2);
                drawLine(grid3, [[8,2], [8, 3], [9,3], [9,4], [10, 4]]);
                drawLine(grid3, [[11, 4], [12,4], [12,5]]);
                drawLine(grid3, [[13, 6], [14,6], [14,7]]);
                drawLine(grid3, [[0,10], [3,8], [5,14]]);
                drawLine(grid3, [[20, 12],[18, 12], [18, 8], [15, 13],[12, 12], [12, 14], [10,14], [11, 16],[5,17]]);
                const grid4 = nodes.filter(d => d.index == 3);
                drawLine(grid4, [[0,10], [3,8], [5,14]]);
                drawLine(grid4, [[8,0],[8,7],[10,5],[10,2], [12,2],[12,4],[14,6]]);
                drawLine(grid4, [[20, 12],[18, 12], [18, 5], [15, 13],[12, 10], [8, 14], [14,15], [11, 18], [8,16],[5,19]]);
            }
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
                    .text('习题解答')
                    .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
                        // this.answer_dialog = true;
                        this.loadAnswer();
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
                if(this.cur_pos == 1) return;
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
                        // this.answer_dialog = true;
                        this.loadAnswer();
                        return;
                    }
                    let mod = 9;
                    if(this.extra) mod == 10
                    if(!this.in_break && (this.cur_pos - this.total_length[0]) % 10 == 0
                        && this.cur_pos != this.total_length[0] + this.total_length[1]
                        && this.cur_pos > this.total_length[0]) {
                        this.breakTime(2);
                        return;
                    }
                }
            }
            await this.changeQuestion(nxt);
        },
        loadAnswer: async function() {
            const that = this;
            await axios.post('/api/get-answer', {
            }).then(function(response) {
                if(response.data.msg === 'Error') {
                    // console.log('Get answer error:', response.data.detail);
                    that.answer_dialog = false;
                }
                else{
                    // console.log('Get Answer', response.data);
                    that.answer_data = response.data.answer;
                    that.answer_dialog = true;
                }
            });
        },
        openDialog: function() {
            setTimeout(() => {
                this.dialogLayout();
                this.dialogRender();
            }, 10);
            // const that = this;
            // await axios.post('/api/get-answer', {
            // }).then(function(response) {
            //     if(response.data.msg === 'Error') {
            //         // console.log('Get answer error:', response.data.detail);
            //         this.answer_dialog = false;
            //     }
            //     else{
            //         // console.log('Get Answer', response.data);
            //         that.answer_data = response.data.answer;
            //         that.dialogLayout();
            //         that.dialogRender();
            //     }
            // });
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
                this.$alert('<p style="font-size:18px;">请阅读知情同意书并<span style="color:red;">同意相关条例</span>。</p>', '注意', {
                    confirmButtonText: '确认',
                    dangerouslyUseHTMLString: true,
                });
            }
        },
        closeTutorial: function() {
            const that = this;
            this.$confirm('<p style="font-size:18px;">您确定要结束教程吗？ </p>\
                <p style="font-size:18px;"><span style="color:red;">界面关闭后您将无法回到该视频。 </span></p>', '注意', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                dangerouslyUseHTMLString: true,
                type: 'warning'
            }).then(() => {
                that.tutorial = false;
                const video = document.getElementById('tutorial')
                video.pause();
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
            let button_y = use_text != 1 ? 620: 700;
            if(use_text == 4) button_y = 700;
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
                .attr('font-family', 'Times, "Times New Roman", "楷体"')
                // .attr('font-weight', 'bold')
                .attr('text-anchor', 'middle')
                .attr('opacity', 0)
                .transition()
                .duration(this.create_duration)
                .attr('opacity', 1)
            if(use_text == 1 || use_text == 4) {
                const tip_data = this.tip_text.map((d, index) => {
                    return {
                        id: index,
                        value: d,
                        x: 700,
                        y: 580 + 35 * index
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
                    .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
                    .text(use_text < 2 || use_text == 4 ? '开始': '继续')
                    .attr('font-family', 'Times, "Times New Roman", "楷体"')
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
        if(this.extra && this.is_first) {
            this.breakTime(4);
            this.enableButton();
            this.consent_form = false;
            this.tutorial = true;
            this.$confirm('本次测试为补充测试，衷心感谢您的参与。\n请确认是否跳过教程和模拟测试？', '提示', {
                confirmButtonText: '跳过',
                cancelButtonText: '取消',
                type: 'warning',
                closeOnClickModal: false,
                closeOnPressEscape: false,
                }).then(() => {
                    this.tutorial = false;
                    this.nxt_index = 6;})
                // }).catch(() => {
                          
                // });
            return;
        }
        if(this.is_first) {
            this.breakTime();
            this.enableButton();
            this.consent_form = true;
            this.tutorial = true;
            return;
        }
        if(this.finish_all) {
            // this.finish_all = false;
            this.breakTime(3);
            this.enableButton();
            return;
        }
        // this.getHackData();
        this.getData();
        // this.$message({
        //   message: '当前版本为正在修改版本，可能存在信息丢失风险，请稍后作答',
        //   type: 'warning'
        // });
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

.el-message-box__title {
    font-family: Times, "Times New Roman", "楷体";
}

.el-message-box__content {
    font-family: Times, "Times New Roman", "楷体";
}

.el-message__content {
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
    word-break: normal;
    word-wrap: break-word;
}

#sheet .el-dialog__body {
    padding-top: 5px;
}

#consent .el-dialog__body {
    padding-top: 15px;
}

</style>