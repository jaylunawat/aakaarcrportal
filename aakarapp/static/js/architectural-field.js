(() => {
    const canvas = document.getElementById('architectural-field');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const finePointer = window.matchMedia('(pointer: fine)').matches;
    const cursor = document.querySelector('.custom-cursor');
    const TAU = Math.PI * 2;
    const palette = {
        cyan: '68,224,207',
        yellow: '255,208,38',
        coral: '255,117,87',
        paper: '244,242,233',
        navy: '5,9,13'
    };

    let width = 0;
    let height = 0;
    let dpr = 1;
    let groundY = 0;
    let sceneScale = 1;
    let scrollY = window.scrollY;
    let previousTime = performance.now();
    let animationFrame = 0;

    const pointer = {
        x: window.innerWidth * .5,
        y: window.innerHeight * .45,
        active: false
    };

    const buildingPlans = [
        { x: .015, width: .15, height: .34, floors: 6, bays: 3, depth: 8, brace: 0 },
        { x: .185, width: .19, height: .56, floors: 10, bays: 4, depth: 11, brace: 1 },
        { x: .40, width: .11, height: .29, floors: 5, bays: 2, depth: 7, brace: 2 },
        { x: .565, width: .17, height: .43, floors: 7, bays: 4, depth: 9, brace: 0 },
        { x: .75, width: .105, height: .63, floors: 11, bays: 2, depth: 10, brace: 1 },
        { x: .87, width: .14, height: .39, floors: 7, bays: 3, depth: 8, brace: 2 }
    ];

    const workers = [
        { anchor: 'building', building: 0, floor: 2, u: .22, task: 'hammer', phase: .3, greet: 0 },
        { anchor: 'building', building: 0, floor: 4, u: .72, task: 'weld', phase: 1.8, greet: 0 },
        { anchor: 'building', building: 1, floor: 3, u: .25, task: 'drill', phase: 2.2, greet: 0 },
        { anchor: 'building', building: 1, floor: 6, u: .70, task: 'hammer', phase: 4.1, greet: 0 },
        { anchor: 'building', building: 1, floor: 9, u: .43, task: 'signal', phase: .9, greet: 0 },
        { anchor: 'building', building: 2, floor: 2, u: .58, task: 'weld', phase: 3.4, greet: 0 },
        { anchor: 'building', building: 3, floor: 2, u: .20, task: 'hammer', phase: 5.4, greet: 0 },
        { anchor: 'building', building: 3, floor: 5, u: .78, task: 'drill', phase: 1.4, greet: 0 },
        { anchor: 'building', building: 4, floor: 4, u: .36, task: 'weld', phase: 2.8, greet: 0 },
        { anchor: 'building', building: 4, floor: 8, u: .68, task: 'hammer', phase: 4.8, greet: 0 },
        { anchor: 'building', building: 5, floor: 3, u: .25, task: 'drill', phase: .6, greet: 0 },
        { anchor: 'building', building: 5, floor: 6, u: .68, task: 'signal', phase: 3.8, greet: 0 },
        { anchor: 'ground', x: .08, task: 'shovel', phase: 2.5, greet: 0 },
        { anchor: 'ground', x: .35, task: 'plan', phase: 4.4, greet: 0 },
        { anchor: 'ground', x: .54, task: 'shovel', phase: .8, greet: 0 },
        { anchor: 'ground', x: .90, task: 'plan', phase: 5.1, greet: 0 },
        { anchor: 'crane', task: 'signal', phase: 1.2, greet: 0 }
    ];

    const machines = [
        { type: 'excavator', progress: .08, direction: 1, speed: 26, greet: 0 },
        { type: 'loader', progress: .66, direction: -1, speed: 18, greet: 0 }
    ];

    const particles = [];

    const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

    const resize = () => {
        width = window.innerWidth;
        height = window.innerHeight;
        dpr = Math.min(window.devicePixelRatio || 1, 1.55);
        sceneScale = clamp(width / 1180, .68, 1.15);
        groundY = height * (width < 620 ? .79 : .86);
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const buildingRect = plan => ({
        x: plan.x * width,
        width: plan.width * width,
        height: plan.height * height,
        top: groundY - plan.height * height,
        depth: plan.depth * sceneScale
    });

    const line = (x1, y1, x2, y2) => {
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    };

    const drawBuilding = (plan, index, time) => {
        const rect = buildingRect(plan);
        const floorHeight = rect.height / plan.floors;
        const bayWidth = rect.width / plan.bays;
        const rearX = rect.x + rect.depth;
        const rearTop = rect.top - rect.depth * .58;

        ctx.save();
        ctx.lineCap = 'square';
        ctx.lineJoin = 'miter';

        const towerFade = ctx.createLinearGradient(0, rect.top, 0, groundY);
        towerFade.addColorStop(0, 'rgba(68,224,207,.22)');
        towerFade.addColorStop(.6, 'rgba(68,224,207,.12)');
        towerFade.addColorStop(1, 'rgba(68,224,207,.055)');
        ctx.strokeStyle = towerFade;
        ctx.lineWidth = .9;

        ctx.strokeRect(rearX, rearTop, rect.width, rect.height);
        ctx.strokeRect(rect.x, rect.top, rect.width, rect.height);
        line(rect.x, rect.top, rearX, rearTop);
        line(rect.x + rect.width, rect.top, rearX + rect.width, rearTop);
        line(rect.x, groundY, rearX, groundY - rect.depth * .58);
        line(rect.x + rect.width, groundY, rearX + rect.width, groundY - rect.depth * .58);

        for (let bay = 1; bay < plan.bays; bay += 1) {
            const frontX = rect.x + bayWidth * bay;
            line(frontX, rect.top, frontX, groundY);
            line(frontX + rect.depth, rearTop, frontX + rect.depth, groundY - rect.depth * .58);
        }

        for (let floor = 1; floor < plan.floors; floor += 1) {
            const y = groundY - floorHeight * floor;
            const rearY = y - rect.depth * .58;
            ctx.strokeStyle = floor % 3 === plan.brace ? 'rgba(255,208,38,.105)' : 'rgba(68,224,207,.12)';
            ctx.lineWidth = floor % 3 === plan.brace ? 1 : .72;
            line(rect.x, y, rect.x + rect.width, y);
            line(rearX, rearY, rearX + rect.width, rearY);
            line(rect.x, y, rearX, rearY);
            line(rect.x + rect.width, y, rearX + rect.width, rearY);

            if ((floor + index) % 3 === 0) {
                ctx.fillStyle = 'rgba(68,224,207,.018)';
                ctx.fillRect(rect.x + 1, y - floorHeight + 1, rect.width - 2, floorHeight - 2);
            }
        }

        ctx.strokeStyle = 'rgba(255,208,38,.085)';
        ctx.lineWidth = .7;
        for (let floor = 0; floor < plan.floors; floor += 2) {
            const y1 = groundY - floorHeight * floor;
            const y2 = groundY - floorHeight * Math.min(plan.floors, floor + 2);
            const startLeft = (floor + index) % 4 < 2;
            line(startLeft ? rect.x : rect.x + rect.width, y1, startLeft ? rect.x + rect.width : rect.x, y2);
        }

        const scaffoldX = index % 2 ? rect.x - 8 * sceneScale : rect.x + rect.width + 8 * sceneScale;
        ctx.strokeStyle = 'rgba(244,242,233,.075)';
        ctx.lineWidth = .55;
        line(scaffoldX, rect.top + floorHeight, scaffoldX, groundY);
        line(scaffoldX + 7 * sceneScale, rect.top + floorHeight, scaffoldX + 7 * sceneScale, groundY);
        for (let floor = 1; floor < plan.floors; floor += 1) {
            const y = groundY - floorHeight * floor;
            line(scaffoldX - 2, y, scaffoldX + 9 * sceneScale, y);
            if (floor % 2) line(scaffoldX, y, scaffoldX + 7 * sceneScale, y + floorHeight);
        }

        ctx.strokeStyle = 'rgba(255,117,87,.14)';
        ctx.lineWidth = .65;
        for (let bay = 0; bay <= plan.bays; bay += 1) {
            const rebarX = rect.x + bayWidth * bay;
            const sway = Math.sin(time * .6 + index + bay) * .35;
            line(rebarX, rect.top, rebarX + sway, rect.top - (7 + (bay % 2) * 4) * sceneScale);
        }

        const workFloor = ((index * 3 + 2) % Math.max(2, plan.floors - 1)) + 1;
        const workY = groundY - workFloor * floorHeight - 3;
        ctx.fillStyle = `rgba(${index % 2 ? palette.yellow : palette.cyan},${.22 + Math.sin(time * 1.1 + index) * .055})`;
        ctx.fillRect(rect.x + rect.width * .14, workY, 3.5 * sceneScale, 1.2 * sceneScale);
        ctx.restore();
    };

    const craneGeometry = time => {
        const x = width * .49;
        const top = height * .13;
        const boomY = top + 18 * sceneScale;
        const boomLeft = Math.max(12, x - width * .22);
        const boomRight = Math.min(width - 12, x + width * .25);
        const trolley = boomLeft + (boomRight - boomLeft) * (.52 + Math.sin(time * .18) * .24);
        return { x, top, boomY, boomLeft, boomRight, trolley };
    };

    const drawCrane = time => {
        const crane = craneGeometry(time);
        const towerWidth = 15 * sceneScale;
        ctx.save();
        ctx.strokeStyle = 'rgba(255,208,38,.16)';
        ctx.lineWidth = .8;
        ctx.strokeRect(crane.x - towerWidth * .5, crane.top, towerWidth, groundY - crane.top);

        const segmentHeight = 22 * sceneScale;
        for (let y = crane.top; y < groundY; y += segmentHeight) {
            line(crane.x - towerWidth * .5, y, crane.x + towerWidth * .5, Math.min(groundY, y + segmentHeight));
            line(crane.x + towerWidth * .5, y, crane.x - towerWidth * .5, Math.min(groundY, y + segmentHeight));
        }

        ctx.strokeStyle = 'rgba(68,224,207,.17)';
        line(crane.boomLeft, crane.boomY, crane.boomRight, crane.boomY);
        line(crane.x, crane.top, crane.boomLeft, crane.boomY);
        line(crane.x, crane.top, crane.boomRight, crane.boomY);
        for (let x = crane.boomLeft; x < crane.boomRight; x += 25 * sceneScale) {
            line(x, crane.boomY, Math.min(crane.boomRight, x + 13 * sceneScale), crane.boomY - 9 * sceneScale);
            line(Math.min(crane.boomRight, x + 13 * sceneScale), crane.boomY - 9 * sceneScale, Math.min(crane.boomRight, x + 25 * sceneScale), crane.boomY);
        }

        const hookY = height * (.37 + Math.sin(time * .31) * .035);
        ctx.strokeStyle = 'rgba(244,242,233,.16)';
        line(crane.trolley, crane.boomY, crane.trolley, hookY);
        ctx.beginPath();
        ctx.arc(crane.trolley, hookY + 3 * sceneScale, 3 * sceneScale, 0, Math.PI * 1.25);
        ctx.stroke();
        ctx.restore();
    };

    const workerPosition = worker => {
        if (worker.anchor === 'ground') {
            return { x: worker.x * width, y: groundY + 1 };
        }
        if (worker.anchor === 'crane') {
            const crane = craneGeometry(performance.now() * .001);
            return { x: crane.x + 12 * sceneScale, y: crane.top + 24 * sceneScale };
        }
        const plan = buildingPlans[worker.building];
        const rect = buildingRect(plan);
        const floorHeight = rect.height / plan.floors;
        return {
            x: rect.x + rect.width * worker.u,
            y: groundY - floorHeight * worker.floor - 1
        };
    };

    const addParticle = (x, y, tone, velocityX, velocityY, life, size, gravity = 10) => {
        if (particles.length > 150) particles.shift();
        particles.push({ x, y, tone, velocityX, velocityY, life, maxLife: life, size, gravity });
    };

    const emitToolParticles = (worker, x, y, time, intensity) => {
        if (worker.greet > .2 || time < (worker.nextParticle || 0) || intensity < .78) return;
        worker.nextParticle = time + (worker.task === 'weld' ? .045 : .18);
        const count = worker.task === 'weld' ? 3 : 2;
        for (let index = 0; index < count; index += 1) {
            const spark = worker.task === 'weld';
            addParticle(
                x,
                y,
                spark ? palette.cyan : palette.yellow,
                (Math.random() - .5) * (spark ? 22 : 10),
                -Math.random() * (spark ? 25 : 11),
                .34 + Math.random() * .28,
                spark ? .8 : 1.25,
                spark ? 21 : 8
            );
        }
    };

    const drawGreeting = (x, y, scale, alpha) => {
        if (alpha < .48) return;
        const bubbleAlpha = clamp((alpha - .48) * 2, 0, 1);
        const bx = x + 7 * scale;
        const by = y - 24 * scale;
        ctx.save();
        ctx.globalAlpha = bubbleAlpha;
        ctx.fillStyle = 'rgba(5,9,13,.9)';
        ctx.strokeStyle = 'rgba(68,224,207,.55)';
        ctx.lineWidth = .7;
        ctx.beginPath();
        ctx.roundRect(bx, by, 18 * scale, 10 * scale, 3 * scale);
        ctx.fill();
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(bx + 3 * scale, by + 10 * scale);
        ctx.lineTo(bx + 1 * scale, by + 13 * scale);
        ctx.lineTo(bx + 7 * scale, by + 10 * scale);
        ctx.fill();
        ctx.fillStyle = 'rgba(244,242,233,.9)';
        ctx.font = `${Math.max(5, 6 * scale)}px monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('HI', bx + 9 * scale, by + 5.2 * scale);
        ctx.restore();
    };

    const drawWorker = (worker, position, time) => {
        const scale = sceneScale * (worker.anchor === 'ground' ? 1.03 : .9);
        const heightUnit = 15 * scale;
        const work = 1 - worker.greet;
        const cycle = Math.sin(time * 4 + worker.phase);
        const x = position.x;
        const y = position.y;
        const headY = y - heightUnit;
        const shoulderY = headY + 4.8 * scale;
        const hipY = y - 4.2 * scale;
        const alpha = .43 + worker.greet * .48;
        const lineColor = `rgba(${palette.paper},${alpha})`;

        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.strokeStyle = lineColor;
        ctx.fillStyle = lineColor;
        ctx.lineWidth = Math.max(.65, .82 * scale);

        ctx.beginPath();
        ctx.arc(x, headY, 1.8 * scale, 0, TAU);
        ctx.fill();
        ctx.strokeStyle = `rgba(${palette.yellow},${.58 + worker.greet * .34})`;
        ctx.beginPath();
        ctx.arc(x, headY - .5 * scale, 2.35 * scale, Math.PI, TAU);
        ctx.stroke();

        ctx.strokeStyle = lineColor;
        line(x, shoulderY, x, hipY);
        line(x, hipY, x - 2.6 * scale, y);
        line(x, hipY, x + 2.8 * scale, y);

        let leftHand = { x: x - 4 * scale, y: shoulderY + 3 * scale };
        let rightHand = { x: x + 4 * scale, y: shoulderY + 3 * scale };
        let toolTip = null;
        let intensity = 0;

        if (worker.task === 'hammer') {
            intensity = (cycle + 1) * .5;
            rightHand = {
                x: x + (3 + cycle * 2.6 * work) * scale,
                y: shoulderY + (2.4 - cycle * 4.2 * work) * scale
            };
            toolTip = { x: rightHand.x + 2.8 * scale, y: rightHand.y - 3.8 * scale };
            line(x, shoulderY, rightHand.x, rightHand.y);
            ctx.strokeStyle = `rgba(${palette.yellow},${alpha})`;
            line(rightHand.x, rightHand.y, toolTip.x, toolTip.y);
            line(toolTip.x - 1.8 * scale, toolTip.y - 1.2 * scale, toolTip.x + 1.8 * scale, toolTip.y + 1.2 * scale);
        } else if (worker.task === 'drill') {
            intensity = Math.abs(Math.sin(time * 10 + worker.phase));
            rightHand = { x: x + 5.5 * scale, y: shoulderY + (2 + intensity * .7 * work) * scale };
            toolTip = { x: rightHand.x + 4 * scale, y: rightHand.y + .4 * scale };
            line(x, shoulderY, rightHand.x, rightHand.y);
            ctx.strokeStyle = `rgba(${palette.cyan},${alpha})`;
            line(rightHand.x, rightHand.y, toolTip.x, toolTip.y);
        } else if (worker.task === 'weld') {
            intensity = (Math.sin(time * 12 + worker.phase) + 1) * .5;
            rightHand = { x: x + 4.8 * scale, y: shoulderY + 4.3 * scale };
            toolTip = { x: rightHand.x + 2.8 * scale, y: rightHand.y + 1.6 * scale };
            line(x, shoulderY, rightHand.x, rightHand.y);
            ctx.strokeStyle = `rgba(${palette.cyan},${alpha})`;
            line(rightHand.x, rightHand.y, toolTip.x, toolTip.y);
        } else if (worker.task === 'shovel') {
            intensity = (cycle + 1) * .5;
            rightHand = { x: x + 3.8 * scale, y: shoulderY + 4 * scale };
            toolTip = { x: x + (7 + cycle * 1.5 * work) * scale, y: y + 1 * scale };
            line(x, shoulderY, rightHand.x, rightHand.y);
            ctx.strokeStyle = `rgba(${palette.yellow},${alpha})`;
            line(rightHand.x, rightHand.y, toolTip.x, toolTip.y);
            line(toolTip.x - 1.5 * scale, toolTip.y, toolTip.x + 1.8 * scale, toolTip.y - 1 * scale);
        } else if (worker.task === 'plan') {
            rightHand = { x: x + 3.8 * scale, y: shoulderY + 3 * scale };
            leftHand = { x: x - 3.8 * scale, y: shoulderY + 3 * scale };
            line(x, shoulderY, rightHand.x, rightHand.y);
            ctx.fillStyle = `rgba(${palette.cyan},${alpha * .42})`;
            ctx.fillRect(leftHand.x, leftHand.y, 7.6 * scale, 3.8 * scale);
            ctx.strokeStyle = `rgba(${palette.paper},${alpha})`;
            ctx.strokeRect(leftHand.x, leftHand.y, 7.6 * scale, 3.8 * scale);
        } else {
            const signal = Math.sin(time * 3 + worker.phase) * 1.4 * scale * work;
            rightHand = { x: x + 4 * scale, y: shoulderY - 3.5 * scale + signal };
            line(x, shoulderY, rightHand.x, rightHand.y);
        }

        line(x, shoulderY, leftHand.x, leftHand.y);

        if (worker.greet > .02) {
            const wave = Math.sin(time * 8.2 + worker.phase) * 2.1 * scale;
            const elbow = { x: x + 3.7 * scale, y: shoulderY - 3.2 * scale };
            const hand = { x: x + 5.5 * scale + wave, y: shoulderY - 8.2 * scale };
            ctx.strokeStyle = `rgba(${palette.paper},${worker.greet * .92})`;
            ctx.lineWidth = 1.05 * scale;
            line(x, shoulderY, elbow.x, elbow.y);
            line(elbow.x, elbow.y, hand.x, hand.y);

            ctx.fillStyle = `rgba(${palette.navy},${worker.greet * .75})`;
            ctx.beginPath();
            ctx.arc(x - .65 * scale, headY, .36 * scale, 0, TAU);
            ctx.arc(x + .65 * scale, headY, .36 * scale, 0, TAU);
            ctx.fill();
        }

        if (toolTip) emitToolParticles(worker, toolTip.x, toolTip.y, time, intensity);
        drawGreeting(x, y, scale, worker.greet);
        ctx.restore();
    };

    const machinePosition = machine => {
        const travel = width + 260 * sceneScale;
        const raw = -130 * sceneScale + machine.progress * travel;
        return {
            x: machine.direction === 1 ? raw : width - raw,
            y: groundY + (machine.type === 'excavator' ? 28 : 51) * sceneScale
        };
    };

    const drawMachineOperator = (machine, localX, localY, time) => {
        ctx.save();
        ctx.fillStyle = `rgba(${palette.paper},${.52 + machine.greet * .42})`;
        ctx.beginPath();
        ctx.arc(localX, localY, 1.9 * sceneScale, 0, TAU);
        ctx.fill();
        ctx.strokeStyle = `rgba(${palette.yellow},.8)`;
        ctx.lineWidth = .8;
        ctx.beginPath();
        ctx.arc(localX, localY - .4 * sceneScale, 2.4 * sceneScale, Math.PI, TAU);
        ctx.stroke();
        if (machine.greet > .04) {
            const wave = Math.sin(time * 8) * 1.5 * sceneScale;
            ctx.strokeStyle = `rgba(${palette.paper},${machine.greet * .9})`;
            line(localX + 1, localY + 2, localX + 4 * sceneScale + wave, localY - 5 * sceneScale);
            drawGreeting(localX, localY + 15 * sceneScale, sceneScale, machine.greet);
        }
        ctx.restore();
    };

    const drawExcavator = (machine, position, time, dt) => {
        ctx.save();
        ctx.translate(position.x, position.y);
        ctx.scale(machine.direction, 1);
        ctx.lineCap = 'round';

        ctx.fillStyle = 'rgba(5,9,13,.8)';
        ctx.strokeStyle = 'rgba(68,224,207,.28)';
        ctx.lineWidth = .9;
        ctx.beginPath();
        ctx.roundRect(-24 * sceneScale, -9 * sceneScale, 48 * sceneScale, 9 * sceneScale, 4 * sceneScale);
        ctx.fill();
        ctx.stroke();
        for (let x = -18; x <= 18; x += 9) {
            ctx.beginPath();
            ctx.arc(x * sceneScale, -4.5 * sceneScale, 2.2 * sceneScale, 0, TAU);
            ctx.stroke();
        }

        ctx.fillStyle = 'rgba(255,208,38,.12)';
        ctx.strokeStyle = 'rgba(255,208,38,.38)';
        ctx.strokeRect(-15 * sceneScale, -18 * sceneScale, 26 * sceneScale, 9 * sceneScale);
        ctx.fillRect(-15 * sceneScale, -18 * sceneScale, 26 * sceneScale, 9 * sceneScale);
        ctx.fillStyle = 'rgba(68,224,207,.08)';
        ctx.strokeStyle = 'rgba(244,242,233,.28)';
        ctx.strokeRect(-10 * sceneScale, -36 * sceneScale, 17 * sceneScale, 18 * sceneScale);
        ctx.fillRect(-10 * sceneScale, -36 * sceneScale, 17 * sceneScale, 18 * sceneScale);

        const bucketMotion = Math.sin(time * .8) * 4 * sceneScale * (1 - machine.greet);
        ctx.strokeStyle = 'rgba(255,208,38,.48)';
        ctx.lineWidth = 2.1 * sceneScale;
        line(5 * sceneScale, -28 * sceneScale, 29 * sceneScale, (-43 + bucketMotion) * sceneScale);
        line(29 * sceneScale, (-43 + bucketMotion) * sceneScale, 42 * sceneScale, (-20 + bucketMotion * .4) * sceneScale);
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(37 * sceneScale, (-20 + bucketMotion * .4) * sceneScale);
        ctx.lineTo(48 * sceneScale, (-19 + bucketMotion * .4) * sceneScale);
        ctx.lineTo(44 * sceneScale, (-12 + bucketMotion * .4) * sceneScale);
        ctx.stroke();

        drawMachineOperator(machine, -2 * sceneScale, -29 * sceneScale, time);
        ctx.restore();

        if (machine.greet < .2 && Math.random() < dt * 7) {
            addParticle(
                position.x - machine.direction * 20 * sceneScale,
                position.y - 2 * sceneScale,
                palette.yellow,
                -machine.direction * (5 + Math.random() * 8),
                -2 - Math.random() * 4,
                .55 + Math.random() * .4,
                1.3 + Math.random() * 1.6,
                -1
            );
        }
    };

    const drawLoader = (machine, position, time, dt) => {
        ctx.save();
        ctx.translate(position.x, position.y);
        ctx.scale(machine.direction, 1);
        ctx.strokeStyle = 'rgba(255,208,38,.34)';
        ctx.fillStyle = 'rgba(255,208,38,.09)';
        ctx.lineWidth = .9;
        ctx.strokeRect(-16 * sceneScale, -20 * sceneScale, 28 * sceneScale, 11 * sceneScale);
        ctx.fillRect(-16 * sceneScale, -20 * sceneScale, 28 * sceneScale, 11 * sceneScale);
        ctx.strokeStyle = 'rgba(68,224,207,.28)';
        ctx.strokeRect(-8 * sceneScale, -32 * sceneScale, 15 * sceneScale, 12 * sceneScale);
        [-10, 9].forEach(x => {
            ctx.fillStyle = 'rgba(5,9,13,.9)';
            ctx.beginPath();
            ctx.arc(x * sceneScale, -5 * sceneScale, 5 * sceneScale, 0, TAU);
            ctx.fill();
            ctx.stroke();
        });
        const lift = Math.sin(time * .65) * 2.5 * sceneScale * (1 - machine.greet);
        ctx.strokeStyle = 'rgba(255,208,38,.42)';
        line(10 * sceneScale, -15 * sceneScale, 28 * sceneScale, (-20 + lift) * sceneScale);
        ctx.strokeRect(25 * sceneScale, (-22 + lift) * sceneScale, 11 * sceneScale, 7 * sceneScale);
        drawMachineOperator(machine, 0, -26 * sceneScale, time);
        ctx.restore();

        if (machine.greet < .2 && Math.random() < dt * 4) {
            addParticle(position.x + machine.direction * 15 * sceneScale, position.y - 2, palette.coral, machine.direction * 4, -3, .55, 1.4, 1);
        }
    };

    const drawParticles = dt => {
        for (let index = particles.length - 1; index >= 0; index -= 1) {
            const particle = particles[index];
            particle.life -= dt;
            if (particle.life <= 0) {
                particles.splice(index, 1);
                continue;
            }
            particle.x += particle.velocityX * dt;
            particle.y += particle.velocityY * dt;
            particle.velocityY += particle.gravity * dt;
            const alpha = clamp(particle.life / particle.maxLife, 0, 1);
            ctx.fillStyle = `rgba(${particle.tone},${alpha * .48})`;
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size * alpha, 0, TAU);
            ctx.fill();
        }
    };

    const drawGround = () => {
        const gradient = ctx.createLinearGradient(0, groundY - 18, 0, height);
        gradient.addColorStop(0, 'rgba(68,224,207,.035)');
        gradient.addColorStop(.26, 'rgba(5,9,13,.18)');
        gradient.addColorStop(1, 'rgba(5,9,13,.74)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, groundY - 18, width, height - groundY + 18);
        ctx.strokeStyle = 'rgba(68,224,207,.12)';
        ctx.lineWidth = .8;
        line(0, groundY, width, groundY);
        ctx.strokeStyle = 'rgba(255,208,38,.045)';
        ctx.setLineDash([3, 14]);
        for (let y = groundY + 22 * sceneScale; y < height; y += 34 * sceneScale) line(0, y, width, y);
        ctx.setLineDash([]);
    };

    const updateGreeting = (entity, position, dt, radius = 76) => {
        const near = pointer.active && Math.hypot(pointer.x - position.x, pointer.y - position.y) < radius * sceneScale;
        const target = near ? 1 : 0;
        const speed = target ? 8.5 : 3.2;
        entity.greet += (target - entity.greet) * Math.min(1, dt * speed);
    };

    const render = now => {
        const dt = Math.min(.04, Math.max(.001, (now - previousTime) / 1000));
        const time = now * .001;
        previousTime = now;
        ctx.clearRect(0, 0, width, height);
        ctx.save();
        ctx.globalCompositeOperation = 'screen';

        drawGround();
        buildingPlans.forEach((building, index) => drawBuilding(building, index, time));
        drawCrane(time);

        workers.forEach(worker => {
            const position = workerPosition(worker);
            updateGreeting(worker, position, dt, 84);
            drawWorker(worker, position, time);
        });

        machines.forEach(machine => {
            let position = machinePosition(machine);
            const operatorOffsetX = machine.type === 'excavator' ? -2 : 0;
            const operatorOffsetY = machine.type === 'excavator' ? -29 : -26;
            const operator = {
                x: position.x + machine.direction * operatorOffsetX * sceneScale,
                y: position.y + operatorOffsetY * sceneScale
            };
            updateGreeting(machine, operator, dt, 94);
            machine.progress += machine.speed * dt * (1 - machine.greet * .96) / (width + 260 * sceneScale);
            if (machine.progress > 1) machine.progress -= 1;
            position = machinePosition(machine);
            if (machine.type === 'excavator') drawExcavator(machine, position, time, dt);
            else drawLoader(machine, position, time, dt);
        });

        drawParticles(dt);
        ctx.restore();

        if (!reduceMotion) animationFrame = requestAnimationFrame(render);
    };

    const updatePointer = event => {
        pointer.x = event.clientX;
        pointer.y = event.clientY;
        pointer.active = true;
        document.body.style.setProperty('--cursor-x', `${event.clientX}px`);
        document.body.style.setProperty('--cursor-y', `${event.clientY}px`);

        if (cursor && finePointer) {
            cursor.style.transform = `translate3d(${event.clientX}px, ${event.clientY}px, 0)`;
            cursor.classList.add('is-visible');
            const target = event.target instanceof Element ? event.target : null;
            const interactive = target?.closest('a, button, [role="button"], summary, label');
            const nativeInput = target?.closest('input, textarea, select, [contenteditable="true"]');
            cursor.classList.toggle('is-hovering', Boolean(interactive));
            cursor.classList.toggle('is-native', Boolean(nativeInput));
        }

        if (reduceMotion) render(performance.now());
    };

    resize();
    render(performance.now());

    window.addEventListener('resize', () => {
        resize();
        if (reduceMotion) render(performance.now());
    }, { passive: true });
    window.addEventListener('scroll', () => { scrollY = window.scrollY; }, { passive: true });
    window.addEventListener('pointermove', updatePointer, { passive: true });
    window.addEventListener('pointerdown', event => {
        updatePointer(event);
        if (cursor) cursor.classList.add('is-active');
    }, { passive: true });
    window.addEventListener('pointerup', () => {
        if (cursor) cursor.classList.remove('is-active');
    }, { passive: true });
    document.documentElement.addEventListener('mouseleave', () => {
        pointer.active = false;
        if (cursor) cursor.classList.remove('is-visible');
    });
    window.addEventListener('blur', () => {
        pointer.active = false;
        if (cursor) cursor.classList.remove('is-visible');
    });

    if (cursor && finePointer && !reduceMotion) document.body.classList.add('cursor-enabled');

    document.addEventListener('visibilitychange', () => {
        if (document.hidden && animationFrame) {
            cancelAnimationFrame(animationFrame);
            animationFrame = 0;
        } else if (!document.hidden && !reduceMotion && !animationFrame) {
            previousTime = performance.now();
            animationFrame = requestAnimationFrame(render);
        }
    });
})();
