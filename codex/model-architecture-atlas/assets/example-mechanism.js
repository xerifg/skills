function refreshDemo(){const x=+document.getElementById('demo-x').value;document.getElementById('demo-output').textContent=`x=${x.toFixed(1)} → ReLU(x)=${Math.max(0,x).toFixed(1)}`}
document.addEventListener('input',e=>{if(e.target.id==='demo-x')refreshDemo()});document.addEventListener('atlas:mode',refreshDemo);refreshDemo();
