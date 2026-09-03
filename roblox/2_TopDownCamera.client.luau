-- Put this LocalScript into StarterPlayer -> StarterPlayerScripts
-- Name: TopDownCamera

local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

local HEIGHT = 22 -- Closer Undertale camera distance
local PITCH_Z = 8

camera.CameraType = Enum.CameraType.Scriptable

RunService.RenderStepped:Connect(function()
    local character = player.Character
    if character and character:FindFirstChild("HumanoidRootPart") then
        local hrp = character.HumanoidRootPart
        local targetPos = hrp.Position
        
        -- Smooth, crisp 2D Undertale follow
        local camPos = targetPos + Vector3.new(0, HEIGHT, PITCH_Z)
        camera.CFrame = CFrame.new(camPos, targetPos)
    end
end)

print("[IN THE PINES] Closer Undertale Camera Activated!")
