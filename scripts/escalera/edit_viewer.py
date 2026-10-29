from pathlib import Path

base = Path(r"D:\Development\panspermia-fase1b")


def edit(rel, pairs):
    p = base / rel
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (rel, old[:70], t.count(old))
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print(rel, "ok")


edit("src/panspermia/record.py", [
    ('''def _resource_frame(state: IslandState) -> jax.Array:
    g = C.RECORD_RES_GRID
    f = C.RESOURCE_GRID // g
    r = state.resources.reshape(g, f, g, f).mean(axis=(1, 3))
    return jnp.clip(r / (2 * C.K_MEAN) * 255, 0, 255).astype(jnp.uint8)
''', '''def _resource_frame(state: IslandState) -> jax.Array:
    g = C.RECORD_RES_GRID
    f = C.RESOURCE_GRID // g
    r = state.resources.reshape(g, f, g, f).mean(axis=(1, 3))
    return jnp.clip(r / (2 * C.K_MEAN) * 255, 0, 255).astype(jnp.uint8)


def _chem_frame(state: IslandState) -> jax.Array:
    g = C.RECORD_RES_GRID
    f = C.RESOURCE_GRID // g
    c = state.chem.reshape(C.N_CHEM, g, f, g, f).mean(axis=(2, 4))
    return jnp.clip(jnp.tanh(c / C.CHEM_OBS_SCALE) * 255, 0, 255).astype(jnp.uint8)
'''),
    ('''        return s, (st, snapshot(s), _resource_frame(s))

    state, (per_step, frames, res) = jax.lax.scan(body, state, None, length=k)
    frames = jax.tree.map(lambda x: x[C.RECORD_STRIDE - 1::C.RECORD_STRIDE], frames)
    res = res[C.RECORD_RES_STRIDE - 1::C.RECORD_RES_STRIDE]
    return state, metrics.epoch_stats(state, per_step), frames, res''',
     '''        return s, (st, snapshot(s), _resource_frame(s), _chem_frame(s))

    state, (per_step, frames, res, chem) = jax.lax.scan(body, state, None, length=k)
    frames = jax.tree.map(lambda x: x[C.RECORD_STRIDE - 1::C.RECORD_STRIDE], frames)
    frames["chem"] = chem[C.RECORD_RES_STRIDE - 1::C.RECORD_RES_STRIDE]
    res = res[C.RECORD_RES_STRIDE - 1::C.RECORD_RES_STRIDE]
    return state, metrics.epoch_stats(state, per_step), frames, res'''),
])

edit("src/panspermia/viewer_static/index.html", [
    ('''      <label><input type="checkbox" id="showAct" checked> comer / morder</label>''',
     '''      <label><input type="checkbox" id="showAct" checked> comer / morder</label>
      <label><input type="checkbox" id="showChem" checked> química (toxina · nutriente · feromona)</label>'''),
    ('''        <span style="--c:#8be38f">comiendo (punto)</span>''',
     '''        <span style="--c:#8be38f">comiendo (punto) · <b style="color:#ffd166">alga tóxica</b></span>
        <span style="--c:#c77dff">emitiendo toxina (anillo)</span>'''),
    ('''    resCtx.putImageData(img, 0, 0);
    ctx.imageSmoothingEnabled = true; ctx.drawImage(resCanvas, 0, 0, W, W);
  }''', '''    if (A.chem && $("showChem").checked) {
      const cbase = ri * 3 * RX * RY, plane = RX * RY;
      for (let x = 0; x < RX; x++) for (let y = 0; y < RY; y++) {
        const q = x * RY + y, p = 4 * (y * RX + x);
        const nut = A.chem[cbase + q] / 255, tox = A.chem[cbase + plane + q] / 255, phe = A.chem[cbase + 2 * plane + q] / 255;
        img.data[p] = Math.min(255, img.data[p] + 230 * tox + 200 * nut);
        img.data[p + 1] = Math.min(255, img.data[p + 1] + 170 * nut);
        img.data[p + 2] = Math.min(255, img.data[p + 2] + 220 * phe);
      }
    }
    resCtx.putImageData(img, 0, 0);
    ctx.imageSmoothingEnabled = true; ctx.drawImage(resCanvas, 0, 0, W, W);
  }'''),
    ('''      if (fl & 1) { ctx.beginPath(); ctx.arc(x, y, Math.max(1, r * .35), 0, 2 * Math.PI); ctx.fillStyle = "#8be38f"; ctx.fill(); }''',
     '''      if (fl & 1) { ctx.beginPath(); ctx.arc(x, y, Math.max(1, r * .35), 0, 2 * Math.PI); ctx.fillStyle = fl & 16 ? "#ffd166" : "#8be38f"; ctx.fill(); }
      if (fl & 8) { ctx.beginPath(); ctx.arc(x, y, r + 4, 0, 2 * Math.PI); ctx.strokeStyle = "#c77dff"; ctx.lineWidth = 1; ctx.stroke(); }'''),
    ('''for (const id of ["color", "showRes", "showSig", "showAct"]) $(id).onchange = draw;''',
     '''for (const id of ["color", "showRes", "showSig", "showAct", "showChem"]) $(id).onchange = draw;'''),
    ('''  { title: "Clados vivos", series: [["clades_alive", "#e79bd6"]] },''',
     '''  { title: "Clados vivos", series: [["clades_alive", "#e79bd6"]] },
  { title: "Emisión de sustancias", series: [["emit_nutrient", "#ffd166", "nutriente"], ["emit_toxin", "#ff6b5a", "toxina"], ["emit_pheromone", "#78beff", "feromona"]] },
  { title: "Ingesta tóxica (fracción)", series: [["toxic_intake_frac", "#ffd166"]] },
  { title: "Muertes por veneno", series: [["deaths_poison", "#c77dff"]] },'''),
])
