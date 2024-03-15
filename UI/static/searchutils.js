
tooltipCallback = function(context) {
    // Tooltip Element
    let tooltipEl = document.getElementById('chartjs-tooltip');
    // Create element on first render
    if (!tooltipEl) {
        tooltipEl = document.createElement('div');
        tooltipEl.id = 'chartjs-tooltip';
        tooltipEl.innerHTML = '<table></table>';
        document.body.appendChild(tooltipEl);
    }

    // Hide if no tooltip
    const tooltipModel = context.tooltip;
    if (tooltipModel.opacity === 0) {
        tooltipEl.style.opacity = 0;
        return;
    }

    // Set caret Position
    tooltipEl.classList.remove('above', 'below', 'no-transform');
    if (tooltipModel.yAlign) {
        tooltipEl.classList.add(tooltipModel.yAlign);
    } else {
        tooltipEl.classList.add('no-transform');
    }

    function getBody(bodyItem) {
        return bodyItem.lines;
    }

    // Set Text
    if (tooltipModel.body) {
        const titleLines = tooltipModel.title || [];
        const bodyLines = tooltipModel.body.map(getBody);

        let innerHtml = '<thead>';

        titleLines.forEach(function(title) {
            innerHtml += '<tr><th>' + title + '</th></tr>';
        });
        innerHtml += '</thead><tbody>';

        bodyLines.forEach(function(body, i) {
            const colors = tooltipModel.labelColors[i];
            let style = 'background:' + colors.backgroundColor;
            style += '; border-color:' + colors.borderColor;
            style += '; border-width: 2px';
            const span = '<span style="' + style + '">' + body + '</span>';
            innerHtml += '<tr><td>' + span + '</td></tr>';
        });
        innerHtml += '</tbody>';

        let tableRoot = tooltipEl.querySelector('table');
        tableRoot.innerHTML = innerHtml;
    }

    const position = context.chart.canvas.getBoundingClientRect();
    const bodyFont = Chart.helpers.toFont(tooltipModel.options.bodyFont);

    // Display, position, and set styles for font
    tooltipEl.style.opacity = 1;
    tooltipEl.style.position = 'absolute';
    tooltipEl.style.left = position.left + window.pageXOffset + tooltipModel.caretX + 'px';
    tooltipEl.style.top = position.top + window.pageYOffset + tooltipModel.caretY + 'px';
    tooltipEl.style.font = bodyFont.string;
    tooltipEl.style.padding = tooltipModel.padding + 'px ' + tooltipModel.padding + 'px';
    tooltipEl.style.pointerEvents = 'none';
    
}

function populateSummary() {
    var data = document.getElementsByName("goodSummary");
    for (const item of data) {
        item.innerHTML = item.textContent
    }

}

function configureDataTable() {
    
    $('#results').DataTable({
        "columnDefs": [
            {
                "targets": 'no-sort',
                "orderable": false,
                "order": []
            },
            {
                target: 5,
                visible: false,
            }
        ],
        "language": {
            "search": "Filter:",
            "searchPlaceholder": "Enter filter text"
        },

        dom: 'Bfrtip',
        buttons: [
            'pageLength',
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print'
        ],
        lengthMenu: [
            [10, 25, 50, 100, -1],
            ['10 rows', '25 rows', '50 rows', '100 rows', 'Show all']
        ]
    });
}


function getChartDatasets() {
    var casefiles = {};
    var datasets = {};

    var table = $('#results').DataTable();
    table
        .column(5, { search: 'applied' })
        .data()
        .each(function (val) {
            parts = val.split("###");
            caseNum = parts[0];
            if (casefiles[caseNum]) {
                casefiles[caseNum].push(parts[1]);
            } else {
                casefiles[caseNum] = [];
                casefiles[caseNum].push(parts[1]);
            }
        });
    
        Object.keys(casefiles).forEach(function (caseNum) {
            datasets[caseNum] = $.map(casefiles[caseNum], function (path) {

            return {
                name: path,
                y: 1,
            };
        });
    });
    
    return datasets;

}

function drawChart(index, caseid, dataset) {
    
    const ctx = document.getElementById('chart' + index);
    document.getElementById('chart' + index + 'div').style.visibility = 'visible';

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: dataset.map(row => row.name),
            datasets: [
                {
                    label: caseid,
                    data: dataset.map(row => row.y)
                }
            ]
        },
        options: {
            
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    position: 'bottom',
                    text: "Case: " + caseid
                },
                colors: {
                    enabled: false
                },
                tooltip: {
                    enabled: false,
                    external: tooltipCallback
                }
            }
        }
    });
    
    
}



function configurerReportTable( selector ) {
    
    $(selector).DataTable({
        "columnDefs": [
            {
                "targets": 'no-sort',
                "orderable": false,
                "order": []
            }
        ],
        "language": {
            "search": "Filter:",
            "searchPlaceholder": "Enter filter text"
        },

        dom: 'Bfrtip',
        buttons: [
            'pageLength',
            'copyHtml5',
            'excelHtml5',
            'csvHtml5',
            'pdfHtml5',
            'print'
        ],
        lengthMenu: [
            [10, 25, 50, 100, -1],
            ['10 rows', '25 rows', '50 rows', '100 rows', 'Show all']
        ]
    });
}
