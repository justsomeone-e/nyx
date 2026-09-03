-- Put this Tool inside StarterPack
-- Name: AcousticGuitar
-- Inside Tool: create a LocalScript named "GuitarController"

local Tool = script.Parent
local chords = {"Em", "A", "G", "Bm"}
local chordIdx = 1

Tool.Activated:Connect(function()
    local chord = chords[chordIdx]
    chordIdx = (chordIdx % #chords) + 1
    print("[GUITAR] Strummed chord: " .. chord .. " in the pines!")
end)
