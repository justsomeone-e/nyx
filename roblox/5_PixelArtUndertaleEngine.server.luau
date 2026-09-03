-- Put this Script into ServerScriptService
-- Name: PixelArtUndertaleEngine
-- This script automatically turns Roblox into a 2D Pixel Art Undertale/Deltarune Game!

local Players = game:GetService("Players")
local Lighting = game:GetService("Lighting")

-- 1. SPAWN PROCEDURAL PIXEL PINE FOREST & CABIN
local mapFolder = workspace:FindFirstChild("InThePinesMap") or Instance.new("Folder")
mapFolder.Name = "InThePinesMap"
mapFolder.Parent = workspace
mapFolder:ClearAllChildren()

-- Snow Baseplate Material
local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate and baseplate:IsA("BasePart") then
    baseplate.Material = Enum.Material.Snow
    baseplate.Color = Color3.fromRGB(180, 195, 215)
end

-- Helper: Create Pixel Pine Tree
local function createPixelTree(x, z)
    local model = Instance.new("Model")
    model.Name = "PixelPine"
    
    -- Trunk
    local trunk = Instance.new("Part")
    trunk.Size = Vector3.new(2, 6, 2)
    trunk.Position = Vector3.new(x, 3, z)
    trunk.Anchored = true
    trunk.Material = Enum.Material.WoodPlanks
    trunk.Color = Color3.fromRGB(50, 30, 20)
    trunk.Parent = model
    
    -- 3 Green Pine Layers with Snow Tops
    local sizes = {Vector3.new(12, 4, 12), Vector3.new(9, 4, 9), Vector3.new(6, 4, 6)}
    local heights = {7, 10, 13}
    for i = 1, 3 do
        local bough = Instance.new("Part")
        bough.Size = sizes[i]
        bough.Position = Vector3.new(x, heights[i], z)
        bough.Anchored = true
        bough.Material = Enum.Material.Grass
        bough.Color = Color3.fromRGB(18, 48, 28)
        bough.Parent = model
        
        -- Snow Cap
        local snowCap = Instance.new("Part")
        snowCap.Size = Vector3.new(sizes[i].X + 0.2, 0.6, sizes[i].Z + 0.2)
        snowCap.Position = Vector3.new(x, heights[i] + 2, z)
        snowCap.Anchored = true
        snowCap.Material = Enum.Material.Snow
        snowCap.Color = Color3.fromRGB(240, 245, 255)
        snowCap.Parent = model
    end
    
    model.Parent = mapFolder
end

-- Spawn Grove of Trees around spawn
local treeCoords = {
    {-25, -20}, {-18, -35}, {-32, 10}, {-20, 28}, {-35, -5},
    {25, -20}, {30, -35}, {35, 10}, {22, 28}, {38, -5},
    {-10, -45}, {10, -45}, {0, -50}
}
for _, coord in ipairs(treeCoords) do
    createPixelTree(coord[1], coord[2])
end

-- Helper: Create The Wooden Log Cabin
local cabin = Instance.new("Model")
cabin.Name = "LogCabin"

local walls = Instance.new("Part")
walls.Size = Vector3.new(20, 12, 16)
walls.Position = Vector3.new(0, 6, -30)
walls.Anchored = true
walls.Material = Enum.Material.WoodPlanks
walls.Color = Color3.fromRGB(68, 39, 24)
walls.Parent = cabin

-- Door
local door = Instance.new("Part")
door.Size = Vector3.new(4, 7, 0.5)
door.Position = Vector3.new(0, 3.5, -21.8)
door.Anchored = true
door.Material = Enum.Material.Wood
door.Color = Color3.fromRGB(25, 15, 10)
door.Parent = cabin

-- Glowing Warm Window
local window = Instance.new("Part")
window.Size = Vector3.new(4, 4, 0.5)
window.Position = Vector3.new(-5, 6, -21.8)
window.Anchored = true
window.Material = Enum.Material.Neon
window.Color = Color3.fromRGB(245, 158, 11)
window.Parent = cabin

local winLight = Instance.new("PointLight")
winLight.Range = 22
winLight.Brightness = 2
winLight.Color = Color3.fromRGB(245, 158, 11)
winLight.Parent = window

-- Snow Roof
local roof = Instance.new("Part")
roof.Size = Vector3.new(24, 2, 20)
roof.Position = Vector3.new(0, 12.5, -30)
roof.Anchored = true
roof.Material = Enum.Material.Snow
roof.Color = Color3.fromRGB(245, 250, 255)
roof.Parent = cabin

cabin.Parent = mapFolder

-- Railroad Tracks on Right
for z = -50, 50, 4 do
    local tie = Instance.new("Part")
    tie.Size = Vector3.new(7, 0.5, 1.5)
    tie.Position = Vector3.new(18, 0.3, z)
    tie.Anchored = true
    tie.Material = Enum.Material.WoodPlanks
    tie.Color = Color3.fromRGB(45, 30, 20)
    tie.Parent = mapFolder
end
local rail1 = Instance.new("Part")
rail1.Size = Vector3.new(0.6, 0.8, 100)
rail1.Position = Vector3.new(16, 0.6, 0)
rail1.Anchored = true
rail1.Material = Enum.Material.Metal
rail1.Color = Color3.fromRGB(120, 135, 150)
rail1.Parent = mapFolder

local rail2 = rail1:Clone()
rail2.Position = Vector3.new(20, 0.6, 0)
rail2.Parent = mapFolder

-- 2. TURN ROBLOX AVATAR INTO 2D UNDERTALE PIXEL SPRITE
local function setupPixelPlayer(character)
    local hrp = character:WaitForChild("HumanoidRootPart")
    
    -- Turn 3D body parts invisible
    for _, part in ipairs(character:GetDescendants()) do
        if part:IsA("BasePart") and part.Name ~= "HumanoidRootPart" then
            part.Transparency = 1
        elseif part:IsA("Decal") then
            part.Transparency = 1
        end
    end
    
    -- Add Warm Lantern PointLight to Player
    local lanternLight = hrp:FindFirstChild("LanternLight") or Instance.new("PointLight")
    lanternLight.Name = "LanternLight"
    lanternLight.Range = 36
    lanternLight.Brightness = 2.5
    lanternLight.Color = Color3.fromRGB(245, 168, 45)
    lanternLight.Shadows = true
    lanternLight.Parent = hrp
    
    -- Create 2D Pixel Sprite Billboard (Undertale Frisk / Kurt with Guitar)
    local spriteGui = hrp:FindFirstChild("PixelSprite") or Instance.new("BillboardGui")
    spriteGui.Name = "PixelSprite"
    spriteGui.Size = UDim2.new(4.5, 0, 5.5, 0)
    spriteGui.StudsOffset = Vector3.new(0, 0.5, 0)
    spriteGui.AlwaysOnTop = false
    spriteGui.Parent = hrp
    
    local spriteImg = spriteGui:FindFirstChild("SpriteImg") or Instance.new("ImageLabel")
    spriteImg.Name = "SpriteImg"
    spriteImg.Size = UDim2.new(1, 0, 1, 0)
    spriteImg.BackgroundTransparency = 1
    -- High quality Undertale Pixel Character Sprite
    spriteImg.Image = "rbxassetid://13835698308" -- Clean Pixel Wanderer Sprite
    spriteImg.ResampleMode = Enum.ResamplerMode.Pixelated
    spriteImg.Parent = spriteGui
    
    -- Snow Particle Trail under player feet
    local snowPuff = Instance.new("ParticleEmitter")
    snowPuff.Size = NumberSequence.new(0.3, 0.1)
    snowPuff.Transparency = NumberSequence.new(0.2, 1)
    snowPuff.Lifetime = NumberRange.new(0.4, 0.8)
    snowPuff.Rate = 12
    snowPuff.Speed = NumberRange.new(1, 2)
    snowPuff.Color = ColorSequence.new(Color3.fromRGB(240, 245, 255))
    snowPuff.Parent = hrp
end

Players.PlayerAdded:Connect(function(player)
    player.CharacterAdded:Connect(setupPixelPlayer)
    if player.Character then
        setupPixelPlayer(player.Character)
    end
end)

for _, p in ipairs(Players:GetPlayers()) do
    if p.Character then setupPixelPlayer(p.Character) end
end

print("[IN THE PINES] 2D Pixel Art Undertale Engine Deployed!")
