

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
                    callbacks: {
                        title: function (tooltipItems) {
                          return tooltipItems[0].parsed.x;
                        },
                        label: function(data) {  return "" }
                    }
                }
            }
        }
    });
    
}