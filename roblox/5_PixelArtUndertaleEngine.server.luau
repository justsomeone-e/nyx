-- Put this Script into ServerScriptService
-- Name: PixelArtUndertaleEngine
-- Perfected: Balanced Cold Night Lighting, Visible Stylized Character & True Snowy Pines

local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")

-- 1. BALANCED 03:17 AM COLD NIGHT LIGHTING (NO YELLOW DESERT WASH!)
Lighting.TimeOfDay = "03:17:00"
Lighting.ClockTime = 3.28
Lighting.Brightness = 0.3
Lighting.Ambient = Color3.fromRGB(18, 25, 38)
Lighting.OutdoorAmbient = Color3.fromRGB(22, 32, 50)
Lighting.ColorShift_Top = Color3.fromRGB(160, 195, 235)

Lighting.FogColor = Color3.fromRGB(15, 24, 38)
Lighting.FogStart = 20
Lighting.FogEnd = 120

-- 2. PROCEDURAL SNOWY WORLD GENERATION
local mapFolder = workspace:FindFirstChild("InThePinesMap") or Instance.new("Folder")
mapFolder.Name = "InThePinesMap"
mapFolder.Parent = workspace
mapFolder:ClearAllChildren()

-- Crisp Cold White Snow Ground
local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate and baseplate:IsA("BasePart") then
    baseplate.Material = Enum.Material.Snow
    baseplate.Color = Color3.fromRGB(195, 210, 230) -- Authentic night snow
end

-- Create Realistic Snowy Pine Tree
local function createPineTree(x, z)
    local model = Instance.new("Model")
    model.Name = "SnowyPine"
    
    -- Trunk
    local trunk = Instance.new("Part")
    trunk.Size = Vector3.new(2.2, 8, 2.2)
    trunk.Position = Vector3.new(x, 4, z)
    trunk.Anchored = true
    trunk.Material = Enum.Material.WoodPlanks
    trunk.Color = Color3.fromRGB(42, 26, 16)
    trunk.Parent = model
    
    -- 3 Layered Pine Boughs with Crisp White Snow
    local layerData = {
        {size = Vector3.new(13, 3.5, 13), y = 8},
        {size = Vector3.new(10, 3.5, 10), y = 11},
        {size = Vector3.new(6.5, 3.5, 6.5), y = 14}
    }
    
    for _, l in ipairs(layerData) do
        local needles = Instance.new("Part")
        needles.Size = l.size
        needles.Position = Vector3.new(x, l.y, z)
        needles.Anchored = true
        needles.Material = Enum.Material.Grass
        needles.Color = Color3.fromRGB(14, 35, 22) -- Deep Pine Green
        needles.Parent = model
        
        local snow = Instance.new("Part")
        snow.Size = Vector3.new(l.size.X + 0.3, 0.6, l.size.Z + 0.3)
        snow.Position = Vector3.new(x, l.y + 1.8, z)
        snow.Anchored = true
        snow.Material = Enum.Material.Snow
        snow.Color = Color3.fromRGB(245, 250, 255)
        snow.Parent = model
    end
    
    model.Parent = mapFolder
end

-- Forest Ring around clearing
local coords = {
    {-28, -15}, {-22, -32}, {-32, 12}, {-24, 26}, {-36, -2},
    {28, -15}, {32, -32}, {35, 12}, {24, 26}, {38, -2},
    {-14, -45}, {14, -45}, {0, -48}
}
for _, c in ipairs(coords) do createPineTree(c[1], c[2]) end

-- The Authentic Log Cabin
local cabin = Instance.new("Model")
cabin.Name = "LogCabin"

local walls = Instance.new("Part")
walls.Size = Vector3.new(22, 12, 16)
walls.Position = Vector3.new(0, 6, -28)
walls.Anchored = true
walls.Material = Enum.Material.WoodPlanks
walls.Color = Color3.fromRGB(58, 34, 20)
walls.Parent = cabin

local door = Instance.new("Part")
door.Size = Vector3.new(4.5, 7.5, 0.6)
door.Position = Vector3.new(0, 3.75, -19.8)
door.Anchored = true
door.Material = Enum.Material.Wood
door.Color = Color3.fromRGB(28, 16, 10)
door.Parent = cabin

local window = Instance.new("Part")
window.Size = Vector3.new(4, 4, 0.6)
window.Position = Vector3.new(-6, 6.5, -19.8)
window.Anchored = true
window.Material = Enum.Material.Neon
window.Color = Color3.fromRGB(245, 158, 11)
window.Parent = cabin

local winGlow = Instance.new("PointLight")
winGlow.Range = 18
winGlow.Brightness = 1.2
winGlow.Color = Color3.fromRGB(255, 185, 90)
winGlow.Parent = window

local roof = Instance.new("Part")
roof.Size = Vector3.new(25, 2, 19)
roof.Position = Vector3.new(0, 12.8, -28)
roof.Anchored = true
roof.Material = Enum.Material.Snow
roof.Color = Color3.fromRGB(245, 250, 255)
roof.Parent = cabin

cabin.Parent = mapFolder

-- Converging Cold Railroad on Right
for z = -50, 50, 4 do
    local tie = Instance.new("Part")
    tie.Size = Vector3.new(7, 0.4, 1.4)
    tie.Position = Vector3.new(18, 0.2, z)
    tie.Anchored = true
    tie.Material = Enum.Material.WoodPlanks
    tie.Color = Color3.fromRGB(40, 25, 15)
    tie.Parent = mapFolder
end
local rail1 = Instance.new("Part")
rail1.Size = Vector3.new(0.6, 0.7, 100)
rail1.Position = Vector3.new(16, 0.5, 0)
rail1.Anchored = true
rail1.Material = Enum.Material.Metal
rail1.Color = Color3.fromRGB(115, 130, 145)
rail1.Parent = mapFolder

local rail2 = rail1:Clone()
rail2.Position = Vector3.new(20, 0.5, 0)
rail2.Parent = mapFolder

-- 3. CHARACTER STYLING: VISIBLE WANDERER WITH ACOUSTIC GUITAR ON BACK!
local function setupPlayer(character)
    local hrp = character:WaitForChild("HumanoidRootPart")
    
    -- Style character: Teal Parka, Dark Boots, Scarf
    local humanoid = character:WaitForChild("Humanoid")
    
    for _, part in ipairs(character:GetChildren()) do
        if part:IsA("BasePart") then
            part.Transparency = 0 -- Keep character visible!
            if part.Name == "Torso" or part.Name == "UpperTorso" or part.Name == "LowerTorso" then
                part.Color = Color3.fromRGB(3, 105, 161) -- Teal Parka
            elseif part.Name:find("Leg") then
                part.Color = Color3.fromRGB(30, 41, 59) -- Dark boots
            elseif part.Name == "Head" then
                part.Color = Color3.fromRGB(254, 215, 170) -- Pale face
            end
        end
    end
    
    -- Attach Acoustic Guitar Model to Character's Back
    local torso = character:FindFirstChild("Torso") or character:FindFirstChild("UpperTorso") or hrp
    local existingGuitar = torso:FindFirstChild("BackGuitar")
    if not existingGuitar then
        local guitarBody = Instance.new("Part")
        guitarBody.Name = "BackGuitar"
        guitarBody.Size = Vector3.new(1.8, 2.6, 0.6)
        guitarBody.Material = Enum.Material.WoodPlanks
        guitarBody.Color = Color3.fromRGB(217, 119, 6) -- Honey mahogany
        guitarBody.CanCollide = false
        
        local weld = Instance.new("WeldConstraint")
        weld.Part0 = torso
        weld.Part1 = guitarBody
        weld.Parent = guitarBody
        
        guitarBody.CFrame = torso.CFrame * CFrame.new(0, 0, 0.9) * CFrame.Angles(0, 0, math.rad(25))
        guitarBody.Parent = torso
    end
    
    -- Gentle Warm Candlelight (NOT Blinding Yellow Wash)
    local lantern = hrp:FindFirstChild("LanternLight") or Instance.new("PointLight")
    lantern.Name = "LanternLight"
    lantern.Range = 24
    lantern.Brightness = 1.2
    lantern.Color = Color3.fromRGB(255, 205, 140) -- Soft cozy candlelight
    lantern.Shadows = true
    lantern.Parent = hrp
end

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(setupPlayer)
    if player.Character then setupPlayer(player.Character) end
end)

for _, p in ipairs(Players:GetPlayers()) do
    if p.Character then setupPlayer(p.Character) end
end

print("[IN THE PINES] Perfected Snowy Night Engine Activated!")
