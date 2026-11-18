function wrappedText(text,limit=31){let result=[],line='',units=0;for(const c of String(text)){const u=c.charCodeAt(0)>255?2:1;if(units+u>limit&&line){result.push(line);line='';units=0}line+=c;units+=u}if(line)result.push(line);return result}
function dimensionText(s){return String(s)}
function moduleSVG(g,color,compact=false){
  const marker='module-arrow-'+(++diagramSerial),cw=380,colStep=460,gap=90;
  const fieldDefs=compact?[['输入','input'],['输出','output']]:[['作用','purpose'],['输入','input'],['输出','output'],['算子 / 执行顺序','operators']];
  const layout=g.boxes.map((b,index)=>{const details=g.details[b[0]],titles=wrappedText(b[3],35);const fields=fieldDefs.map(([label,key])=>({label,key,lines:wrappedText(dimensionText(details[key]),44)}));const height=32+titles.length*22+fields.reduce((h,f)=>h+45+f.lines.length*19,0);return {b,index,titles,fields,height}});
  const rowCount=Math.max(...g.boxes.map(b=>b[2]))+1,rowHeights=Array(rowCount).fill(0);
  layout.forEach(o=>rowHeights[o.b[2]]=Math.max(rowHeights[o.b[2]],o.height));
  const ys=[];let height=20;rowHeights.forEach(h=>{ys.push(height);height+=h+gap});height-=gap-20;
  const cols=Math.max(...g.boxes.map(b=>b[1]))+1,width=cols*colStep-40;
  layout.forEach(o=>{o.x=20+o.b[1]*colStep;o.y=ys[o.b[2]]});
  const svg=el('svg',{viewBox:`0 0 ${width} ${height}`,width,height,style:`--natural-width:${width}px`,class:'module-svg',role:'img','aria-label':g.title+(compact?'；各模块输入输出维度。':'；每节点标有作用、输入输出维度及算子顺序。')});
  svg.append(el('title',{},g.title));
  const defs=el('defs'),m=el('marker',{id:marker,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:7,markerHeight:7,orient:'auto'});m.append(el('path',{d:'M0 0L10 5L0 10Z',fill:'#7188a2'}));defs.append(m);svg.append(defs);
  const boxes=Object.fromEntries(layout.map(o=>[o.b[0],o]));
  const lineGroup=el('g',{'aria-hidden':'true'});
  for(const [from,to,label] of g.edges){const a=boxes[from],b=boxes[to];let path,lx,ly;
    if(a.b[2]===b.b[2]){const right=b.x>a.x,sx=right?a.x+cw:a.x,tx=right?b.x:b.x+cw;const midY=Math.min(a.y+a.height/2,b.y+b.height/2);path=`M${sx} ${midY}H${tx}`;lx=(sx+tx)/2;ly=midY-12;}
    else if(b.b[2]-a.b[2]===1){const mid=ys[b.b[2]]-gap/2;path=`M${a.x+cw/2} ${a.y+a.height}V${mid}H${b.x+cw/2}V${b.y}`;lx=(a.x+b.x)/2+cw/2;ly=mid-9;}
    else {const gutter=a.x+cw+34;path=`M${a.x+cw/2} ${a.y+a.height}V${a.y+a.height+24}H${gutter}V${b.y-25}H${b.x+cw/2}V${b.y}`;lx=gutter+6;ly=b.y-36;}
    lineGroup.append(el('path',{d:path,fill:'none',stroke:'#7188a2','stroke-width':2,'marker-end':`url(#${marker})`,'stroke-dasharray':label==='identity'?'7 5':'none'}));
    if(label)lineGroup.append(el('text',{x:lx,y:ly,'text-anchor':'middle',class:'module-edge-label'},label));
  }svg.append(lineGroup);
  for(const o of layout){const [id,col,row,title,kind]=o.b,group=el('g',{transform:`translate(${o.x},${o.y})`,'data-op':id});let fill='#ffffff',stroke='#b9cadd';if(kind==='input'||kind==='output'){fill=color+'0c';stroke=color}if(kind==='merge'){fill='#f7f3fc';stroke='#9579ba'}
    group.append(el('rect',{width:cw,height:o.height,rx:10,fill,stroke,'stroke-width':1.5}));
    let y=29;o.titles.forEach((line,i)=>{group.append(el('text',{x:16,y,class:'module-op-title'},(i===0?String(o.index+1).padStart(2,'0')+' · ':'')+line));y+=22});
    for(const f of o.fields){y+=19;group.append(el('text',{x:16,y,class:'module-field-label','data-field-label':f.key},f.label));y+=21;f.lines.forEach(line=>{group.append(el('text',{x:16,y,class:'module-op-body','data-field':f.key},line));y+=19});y+=5;}
    group.append(el('title',{},title+'；'+fieldDefs.map(([label,key])=>label+'：'+dimensionText(g.details[id][key])).join('；')));svg.append(group);
  }
  return svg.outerHTML;
}
