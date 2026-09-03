-- Put this Script into ServerScriptService
-- Name: AtmosphereSetup

local Lighting = game:GetService("Lighting")

Lighting.TimeOfDay = "03:17:00"
Lighting.ClockTime = 3.28
Lighting.Brightness = 0.45
Lighting.Ambient = Color3.fromRGB(15, 20, 30)
Lighting.OutdoorAmbient = Color3.fromRGB(20, 30, 45)

Lighting.FogColor = Color3.fromRGB(12, 20, 32)
Lighting.FogStart = 15
Lighting.FogEnd = 110

local atmosphere = Lighting:FindFirstChildOfClass("Atmosphere")
if not atmosphere then
    atmosphere = Instance.new("Atmosphere")
    atmosphere.Parent = Lighting
end
atmosphere.Density = 0.52
atmosphere.Offset = 0.2
atmosphere.Color = Color3.fromRGB(25, 40, 60)
atmosphere.Decay = Color3.fromRGB(10, 15, 25)
atmosphere.Haze = 2.5

local baseplate = workspace:FindFirstChild("Baseplate")
if baseplate and baseplate:IsA("BasePart") then
    baseplate.Material = Enum.Material.Snow
    baseplate.Color = Color3.fromRGB(226, 232, 240)
end

print("[IN THE PINES] 03:17 AM Winter Atmosphere Initialized!")
