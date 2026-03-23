/**
 * Loan Calculator Logic for Vehicle Vault
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inputs
    const amountSlider = document.getElementById('amountSlider');
    const tenureSlider = document.getElementById('tenureSlider');
    const rateSlider = document.getElementById('rateSlider');

    // Displays
    const amountDisplay = document.getElementById('amountDisplay');
    const tenureDisplay = document.getElementById('tenureDisplay');
    const rateDisplay = document.getElementById('rateDisplay');

    // Results
    const emiResult = document.getElementById('emiResult');
    const totalInterestResult = document.getElementById('totalInterestResult');
    const totalAmountResult = document.getElementById('totalAmountResult');

    let loanChart;

    function formatCurrency(val) {
        return '₹ ' + new Intl.NumberFormat('en-IN').format(val);
    }

    function calculateEMI() {
        const P = parseFloat(amountSlider.value);
        const R = parseFloat(rateSlider.value) / 12 / 100;
        const N = parseInt(tenureSlider.value);

        // EMI Formula: [P x R x (1+R)^N]/[(1+R)^N-1]
        const emi = (P * R * Math.pow(1 + R, N)) / (Math.pow(1 + R, N) - 1);
        const totalAmount = emi * N;
        const totalInterest = totalAmount - P;

        // Update UI
        amountDisplay.textContent = formatCurrency(P);
        tenureDisplay.textContent = N + ' Months';
        rateDisplay.textContent = rateSlider.value + '%';

        emiResult.textContent = formatCurrency(Math.round(emi));
        totalInterestResult.textContent = formatCurrency(Math.round(totalInterest));
        totalAmountResult.textContent = formatCurrency(Math.round(totalAmount));

        updateChart(P, totalInterest);
    }

    function updateChart(principal, interest) {
        const ctx = document.getElementById('loanChart').getContext('2d');
        
        if (loanChart) {
            loanChart.data.datasets[0].data = [principal, interest];
            loanChart.update();
        } else {
            loanChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Principal', 'Interest'],
                    datasets: [{
                        data: [principal, interest],
                        backgroundColor: ['#38bdf8', '#1e293b'],
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#f8fafc',
                                font: {
                                    family: "'Poppins', sans-serif",
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    cutout: '70%'
                }
            });
        }
    }

    // Event Listeners
    if (amountSlider) {
        amountSlider.addEventListener('input', calculateEMI);
        tenureSlider.addEventListener('input', calculateEMI);
        rateSlider.addEventListener('input', calculateEMI);

        // Initial Calc
        calculateEMI();
    }
});
